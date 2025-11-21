"""
Functional test: Quick Start workflow from README

This test mirrors the Quick Start documentation by:
1. Creating a Python agent with a fetch_url skill and summarize reasoner
2. Registering the agent with the AgentField control plane
3. Executing the summarize reasoner via the control plane API
4. Verifying the agent can read live content and summarize it with OpenRouter
"""

import asyncio
import os
import socket
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Dict, Optional, Tuple

import pytest
import requests
import uvicorn


AGENT_BIND_HOST = os.environ.get("TEST_AGENT_BIND_HOST", "127.0.0.1")
AGENT_CALLBACK_HOST = os.environ.get("TEST_AGENT_CALLBACK_HOST", "127.0.0.1")
QUICK_START_URL = os.environ.get("TEST_QUICK_START_URL")

EXAMPLE_DOMAIN_HTML = """<!doctype html>
<html>
<head>
    <title>Example Domain</title>
    <meta charset="utf-8" />
    <meta http-equiv="Content-type" content="text/html; charset=utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
</head>
<body>
    <div>
        <h1>Example Domain</h1>
        <p>This domain is for use in illustrative examples in documents. You may use this
        domain in literature without prior coordination or asking for permission.</p>
        <p><a href="https://www.iana.org/domains/example">More information...</a></p>
    </div>
</body>
</html>
"""


def _start_example_domain_server() -> Tuple[ThreadingHTTPServer, threading.Thread, str]:
    """
    Spin up a lightweight HTTP server that serves the Example Domain HTML used in docs.
    """

    class ExampleDomainHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(EXAMPLE_DOMAIN_HTML.encode("utf-8"))

        def log_message(self, *_):
            # Silence default logging noise from BaseHTTPRequestHandler
            return

    server = ThreadingHTTPServer(("127.0.0.1", 0), ExampleDomainHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address
    return server, thread, f"http://{host}:{port}"


@pytest.mark.functional
@pytest.mark.openrouter
@pytest.mark.asyncio
async def test_quick_start_documentation_flow(
    make_test_agent,
    openrouter_config,
    async_http_client,
):
    """
    Validate the README Quick Start instructions end-to-end.

    This spins up the canonical agent from the docs (fetch_url + summarize),
    registers it with the control plane, runs a live summary request against
    https://example.com, and ensures the response structure matches expectations.
    """
    content_server: Optional[ThreadingHTTPServer] = None
    content_thread: Optional[threading.Thread] = None

    # Determine which URL to summarize. Default to local Example Domain server
    # to avoid relying on outbound internet access, but allow overriding via env.
    if QUICK_START_URL:
        target_url = QUICK_START_URL
    else:
        content_server, content_thread, target_url = _start_example_domain_server()

    # ----------------------------------------------------------------------
    # Step 1: Create the Quick Start agent with OpenRouter configuration
    # ----------------------------------------------------------------------
    agent = make_test_agent(
        node_id="quick-start-agent",
        ai_config=openrouter_config,
    )

    # ----------------------------------------------------------------------
    # Step 2: Define the fetch_url skill and summarize reasoner
    # ----------------------------------------------------------------------
    @agent.skill()
    def fetch_url(url: str) -> str:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text

    @agent.reasoner()
    async def summarize(url: str) -> Dict[str, str]:
        """
        Quick Start reasoner: fetch a URL and summarize it with OpenRouter.
        """
        content = fetch_url(url)
        truncated = content[:2000]  # keep context manageable for the model

        ai_response = await agent.ai(
            system=(
                "You summarize documentation for internal verification. "
                "Always mention the phrase 'Example Domain' exactly once."
            ),
            user=(
                "Summarize the following web page in no more than two sentences. "
                "Focus on what the site is intended for.\n"
                f"Content:\n{truncated}"
            ),
        )
        summary_text = getattr(ai_response, "text", str(ai_response)).strip()

        return {
            "url": url,
            "summary": summary_text,
            "content_snippet": truncated[:200],
        }

    # ----------------------------------------------------------------------
    # Step 3: Start the agent server on a free port
    # ----------------------------------------------------------------------
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((AGENT_BIND_HOST, 0))
        agent_port = s.getsockname()[1]

    agent.base_url = f"http://{AGENT_CALLBACK_HOST}:{agent_port}"

    config = uvicorn.Config(
        app=agent,
        host=AGENT_BIND_HOST,
        port=agent_port,
        log_level="error",
        access_log=False,
    )
    server = uvicorn.Server(config)
    loop = asyncio.new_event_loop()

    def run_server():
        asyncio.set_event_loop(loop)
        loop.run_until_complete(server.serve())

    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()

    # Give uvicorn a moment to start
    await asyncio.sleep(2)

    try:
        # ------------------------------------------------------------------
        # Step 4: Register agent with the control plane
        # ------------------------------------------------------------------
        await agent.agentfield_handler.register_with_agentfield_server(agent_port)
        agent.agentfield_server = None

        # Wait for registration propagation
        await asyncio.sleep(2)

        nodes_response = await async_http_client.get(f"/api/v1/nodes/{agent.node_id}")
        assert nodes_response.status_code == 200, nodes_response.text

        node_data = nodes_response.json()
        assert node_data["id"] == agent.node_id
        assert "summarize" in [r["id"] for r in node_data.get("reasoners", [])]

        # ------------------------------------------------------------------
        # Step 5: Execute the Quick Start reasoner through control plane
        # ------------------------------------------------------------------
        execution_request = {"input": {"url": target_url}}

        execution_response = await async_http_client.post(
            f"/api/v1/reasoners/{agent.node_id}.summarize",
            json=execution_request,
            timeout=90.0,
        )

        assert execution_response.status_code == 200, execution_response.text
        result_data = execution_response.json()

        # ------------------------------------------------------------------
        # Step 6: Validate summary output and metadata
        # ------------------------------------------------------------------
        assert "result" in result_data
        result = result_data["result"]

        assert result["url"] == target_url
        summary_text = result["summary"]
        assert summary_text, "Summary should not be empty"
        assert len(summary_text.split()) >= 5, "Summary should contain multiple words"

        snippet = result.get("content_snippet", "")
        assert "Example Domain" in snippet, "Snippet should contain fetched page content"
        assert len(snippet) > 0

        assert result_data["node_id"] == agent.node_id
        assert result_data["duration_ms"] > 0

        headers = execution_response.headers
        assert "X-Workflow-ID" in headers or "x-workflow-id" in headers
        assert "X-Execution-ID" in headers or "x-execution-id" in headers

    finally:
        # ------------------------------------------------------------------
        # Cleanup: Stop agent server
        # ------------------------------------------------------------------
        server.should_exit = True
        if loop.is_running():
            loop.call_soon_threadsafe(lambda: None)
        thread.join(timeout=10)

        if content_server:
            content_server.shutdown()
            if content_thread:
                content_thread.join(timeout=5)
