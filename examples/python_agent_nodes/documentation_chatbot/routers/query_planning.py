"""Query planning router for documentation chatbot."""

from agentfield import AgentRouter
from schemas import QueryPlan

# Create router with prefix "query"
# This will transform function names: plan_queries -> query_plan_queries
query_router = AgentRouter(prefix="query")


@query_router.reasoner()
async def plan_queries(question: str) -> QueryPlan:
    """Generate 3-5 diverse search queries from the user's question."""

    # Product context for better query generation
    PRODUCT_CONTEXT = """
## Product Overview
AgentField is a Kubernetes-style control plane with IAM for building next generation of autonomous software. It provides production infrastructure
for deploying, orchestrating, and observing multi-agent systems with cryptographic identity and audit trails.

**Architecture**: Distributed control plane + independent agent nodes. Think "Kubernetes for AI agents."

**Positioning**: AgentField is infrastructure, not an application framework. While agent frameworks help you build
single AI applications, AgentField provides the orchestration layer for
deploying and managing distributed multi-agent systems in production (like Kubernetes orchestrates containers).

## Design Philosophy

**Infrastructure-First Approach:**
- Control plane handles routing, identity, memory, and observability centrally
- Agents run as independent microservices, not embedded libraries
- Teams deploy agents independently without coordination
- Every agent function becomes a REST API automatically
- Stateless control plane enables horizontal scaling

**Production-Grade Guarantees:**
- Cryptographic identity for every agent and execution (W3C DID standard)
- Tamper-proof audit trails via Verifiable Credentials
- Zero-config distributed state management
- No timeout limits for async workflows (hours or days)
- Observable by default (workflow DAGs, execution traces, agent notes)

**Built for Multi-Team Scale:**
- Independent agent deployment (no monolithic coordination)
- Service discovery through control plane
- Shared memory fabric across distributed agents
- Cross-agent communication via REST APIs
- Works with any tech stack (Python, Go, React, mobile, .NET, etc.)

## Core Concepts & Terminology

**Agent Primitives:**
- **Reasoners**: AI-guided decision making functions (use LLMs for judgment)
- **Skills**: Deterministic functions (reliable execution, no AI)
- **Agent Nodes**: Independent services that register with the control plane
- **Control Plane**: Central orchestration server (handles routing, memory, identity)

**Identity & Trust:**
- **DIDs** (Decentralized Identifiers): Cryptographic identity for agents (W3C standard)
- **VCs** (Verifiable Credentials): Tamper-proof execution records (W3C standard)
- **Workflow DAGs**: Visual representation of agent execution chains
- **Security Model**: Every execution cryptographically signed and attributable
- **Audit Compliance**: Exportable proof chains for regulatory/compliance requirements
- **Zero-Trust Architecture**: Agents authenticate via DIDs, not shared secrets

**State Management:**
- **Memory Scopes**: Hierarchical state sharing (global, actor, session, workflow)
- **Zero-config memory**: Automatic state synchronization across distributed agents
- **Memory events**: Real-time reactive patterns (on_change listeners)

**Execution Patterns:**
- **Sync execution**: `/api/v1/execute/` (90 second timeout)
- **Async execution**: `/api/v1/execute/async/` (no timeout limits, hours/days)
- **Webhooks**: Callback URLs for async results
- **Cross-agent calls**: `app.call("agent.function")` for agent-to-agent communication

**Scalability & Production Architecture:**
- **Stateless Control Plane**: No session affinity, horizontal scaling to billions of requests
- **Independent Agent Scaling**: Each agent scales independently based on its load
- **Zero Coordination Overhead**: Agents don't need to know about each other to deploy
- **Deployment Flexibility**: Laptop → Docker → Kubernetes with same codebase, zero rewrites
- **Storage Tiers**: Local (SQLite/BoltDB) for dev, PostgreSQL for production/cloud
- **Failure Isolation**: Agent failures don't cascade; control plane handles routing around issues

**CLI Commands:**
- `af init`: Create new agent (Python or Go)
- `af server`: Start control plane
- `af run`: Run agent locally
- `af dev`: Development mode with hot reload

**Key APIs:**
- `app.ai()`: LLM calls with structured output (Pydantic schemas)
- `app.memory`: State management (get/set/on_change)
- `app.call()`: Cross-agent communication
- `app.note()`: Observable execution notes

## Common Topics & Questions

**Getting Started:**
- Installation and setup (af init, af server)
- Creating first agent (Python vs Go choice)
- Understanding reasoners vs skills
- Basic agent structure and configuration

**Agent Development:**
- Registering reasoners and skills
- Using app.ai() for LLM integration
- Structured output with Pydantic/Go structs
- Router pattern for organizing code
- Agent notes and observability

**Multi-Agent Coordination:**
- Cross-agent communication patterns
- Shared memory and state management
- Memory scopes (when to use which)
- Event-driven workflows with memory.on_change

**Production Deployment:**
- Local development (embedded SQLite/BoltDB)
- Docker deployment
- Kubernetes deployment
- Environment variables and configuration

**Identity & Security:**
- DID generation and management
- Verifiable Credentials for audit trails
- Cryptographic proof of execution

**Advanced Features:**
- Async execution for long-running tasks
- Webhook integration
- Custom memory providers
- Performance optimization
- Testing strategies

## Documentation Structure

The documentation is organized by:
- **Getting Started**: Quick start, installation, first agent
- **Core Concepts**: Reasoners, skills, memory, identity, cross-agent communication
- **Guides**: Deployment, testing, multi-agent patterns, examples
- **API Reference**: Python SDK, Go SDK, CLI commands, REST APIs
- **Examples**: Customer support, research assistant, terminal assistant

## Search Term Relationships

When users ask about:
- "Identity" or "authentication" or "security" → Look for: DIDs, Verifiable Credentials, cryptographic identity, audit trails, W3C standards
- "State" or "data sharing" → Look for: memory, scopes, cross-agent memory
- "Setup" or "getting started" → Look for: installation, af init, quick start
- "Deployment" or "production" → Look for: Docker, Kubernetes, local development, scaling
- "Agent communication" → Look for: app.call, cross-agent, workflows
- "Long-running tasks" → Look for: async execution, webhooks
- "Functions" or "endpoints" → Look for: reasoners, skills, API endpoints
- "Differences" or "comparison" or "vs" → Look for: infrastructure vs framework, control plane vs embedded library, multi-team vs single app, production features
- "Scale" or "scalability" → Look for: stateless control plane, independent scaling, billions of requests, horizontal scaling
- "Architecture" → Look for: distributed architecture, control plane, agent nodes, microservices, stateless design
"""

    return await query_router.ai(
        system=(
            "You are a query planning expert for documentation search. "
            "Your job is to generate 3-5 DIVERSE search queries that maximize retrieval coverage.\n\n"
            "## PRODUCT CONTEXT\n"
            f"{PRODUCT_CONTEXT}\n\n"
            "Use this context to understand product-specific terminology and generate better search queries. "
            "For example, if a user asks about 'identity', recognize they likely mean DIDs/VCs. "
            "If they ask about 'functions', they might mean reasoners or skills.\n\n"
            "## DIVERSITY STRATEGIES\n"
            "1. Use different terminology and synonyms (including product-specific terms)\n"
            "2. Cover different aspects (setup, usage, troubleshooting, configuration)\n"
            "3. Range from broad concepts to specific terms\n"
            "4. Include related concepts using the 'Search Term Relationships' above\n"
            "5. Avoid redundancy - each query should target unique angles\n\n"
            "## QUERY TYPES\n"
            "- How-to queries: 'how to install X', 'how to create X'\n"
            "- Concept queries: 'X architecture', 'what is X'\n"
            "- Troubleshooting: 'X error', 'X not working'\n"
            "- Configuration: 'X settings', 'configure X'\n"
            "- API/Reference: 'X API', 'X methods'\n"
            "- Comparison: 'X vs Y', 'when to use X'"
        ),
        user=(
            f"Question: {question}\n\n"
            "Generate 3-5 diverse search queries that cover different angles of this question. "
            "Use your knowledge of the product (AgentField) to include relevant technical terms. "
            "Also specify the strategy: 'broad' (general exploration), 'specific' (targeted search), "
            "or 'mixed' (combination of both)."
        ),
        schema=QueryPlan,
    )
