# Product Requirements Document: Discovery API - Control Plane

**Version:** 1.0
**Date:** November 23, 2025
**Status:** Draft
**Owner:** AgentField Platform Team

---

## 1. Executive Summary

### 1.1 Purpose

The Discovery API enables developers and AI systems to dynamically discover and query available agent capabilities (reasoners and skills) from the AgentField control plane. This is critical for building intelligent AI orchestrators that can make just-in-time decisions about which agents, reasoners, or skills to invoke based on runtime requirements.

### 1.2 Problem Statement

Currently, developers and AI systems must:
- Manually track which agents are available and their capabilities
- Hardcode agent targets in their applications
- Have no programmatic way to discover reasoners/skills and their schemas
- Cannot build dynamic AI orchestrators that select tools at runtime

### 1.3 Success Criteria

- AI orchestrators can discover capabilities in <100ms (p95)
- Supports filtering by wildcards, tags, and agent IDs
- Returns schemas in multiple formats (JSON, XML, Compact)
- Scales to 1000+ concurrent discovery requests
- Zero-downtime deployments with caching

---

## 2. Goals & Non-Goals

### 2.1 Goals

✅ **Primary Goals:**
1. Provide a single, efficient REST endpoint for capability discovery
2. Support wildcard pattern matching for flexible filtering
3. Enable schema discovery for dynamic validation
4. Support multiple output formats for different use cases
5. Maintain high performance through intelligent caching
6. Provide clear, actionable error messages

✅ **Secondary Goals:**
1. Support filtering by multiple agent IDs simultaneously
2. Allow alias query parameters (`agent`/`node_id`, `agent_ids`/`node_ids`)
3. Enable tag-based filtering with wildcard support
4. Provide compact responses for bandwidth-constrained scenarios

### 2.2 Non-Goals

❌ **Out of Scope for v1:**
- Semantic/natural language search
- Performance metrics and analytics
- Cost estimation per capability
- Team-based filtering (no team concept yet)
- MCP server tool discovery
- WebSocket streaming for capability changes
- Authentication/authorization (handled at API gateway level)

---

## 3. API Specification

### 3.1 Endpoint

```
GET /api/v1/discovery/capabilities
```

**Purpose:** Discover available agent capabilities with flexible filtering and schema options.

### 3.2 Query Parameters

| Parameter                 | Type    | Required | Description                                                 | Examples                                     |
| ------------------------- | ------- | -------- | ----------------------------------------------------------- | -------------------------------------------- |
| `agent`<br>`node_id`      | string  | No       | Filter by single agent ID (aliased)                         | `?agent=agent-001`<br>`?node_id=agent-001`   |
| `agent_ids`<br>`node_ids` | string  | No       | Filter by multiple agent IDs (comma-separated, aliased)     | `?agent_ids=agent-1,agent-2`                 |
| `reasoner`                | string  | No       | Filter reasoners by pattern (supports wildcards)            | `?reasoner=*research*`<br>`?reasoner=deep_*` |
| `skill`                   | string  | No       | Filter skills by pattern (supports wildcards)               | `?skill=web_*`                               |
| `tags`                    | string  | No       | Filter by tags (comma-separated, supports wildcards)        | `?tags=ml,nlp`<br>`?tags=ml*,*research`      |
| `include_input_schema`    | boolean | No       | Include input schemas (default: false)                      | `?include_input_schema=true`                 |
| `include_output_schema`   | boolean | No       | Include output schemas (default: false)                     | `?include_output_schema=true`                |
| `include_descriptions`    | boolean | No       | Include descriptions (default: true)                        | `?include_descriptions=false`                |
| `include_examples`        | boolean | No       | Include usage examples (default: false)                     | `?include_examples=true`                     |
| `format`                  | string  | No       | Response format: `json`, `xml`, `compact` (default: json)   | `?format=xml`                                |
| `health_status`           | string  | No       | Filter by health status: `active`, `inactive`, `degraded`   | `?health_status=active`                      |
| `limit`                   | integer | No       | Maximum number of agents to return (default: 100, max: 500) | `?limit=50`                                  |
| `offset`                  | integer | No       | Pagination offset (default: 0)                              | `?offset=100`                                |

### 3.3 Wildcard Pattern Matching

**Valid Patterns:**
- `*abc*` - Contains "abc" anywhere
- `abc*` - Starts with "abc"
- `*abc` - Ends with "abc"
- `abc` - Exact match (no wildcards)

**Examples:**
- `?reasoner=*research*` → Matches: `deep_research`, `web_researcher`, `research_agent`
- `?tags=ml*` → Matches tags: `ml`, `mlops`, `ml_vision`
- `?skill=web_*` → Matches: `web_search`, `web_scraper`, `web_parser`

### 3.4 Response Format (JSON - Default)

```json
{
  "discovered_at": "2025-11-23T10:30:00Z",
  "total_agents": 5,
  "total_reasoners": 23,
  "total_skills": 45,
  "pagination": {
    "limit": 100,
    "offset": 0,
    "has_more": false
  },
  "capabilities": [
    {
      "agent_id": "agent-research-001",
      "base_url": "http://agent-research:8080",
      "version": "2.3.1",
      "health_status": "active",
      "deployment_type": "long_running",
      "last_heartbeat": "2025-11-23T10:29:45Z",

      "reasoners": [
        {
          "id": "deep_research",
          "description": "Performs comprehensive research using multiple sources and synthesizes findings",
          "tags": ["research", "ml", "synthesis"],

          "input_schema": {
            "type": "object",
            "properties": {
              "query": {
                "type": "string",
                "description": "Research query or topic"
              },
              "depth": {
                "type": "integer",
                "minimum": 1,
                "maximum": 5,
                "default": 3,
                "description": "Research depth level"
              },
              "sources": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Specific sources to search"
              }
            },
            "required": ["query"]
          },

          "output_schema": {
            "type": "object",
            "properties": {
              "findings": {
                "type": "array",
                "items": {"type": "object"}
              },
              "confidence": {
                "type": "number",
                "minimum": 0,
                "maximum": 1
              },
              "citations": {
                "type": "array",
                "items": {"type": "string"}
              }
            }
          },

          "examples": [
            {
              "name": "Basic research query",
              "input": {
                "query": "Latest advances in quantum computing",
                "depth": 3
              },
              "description": "Performs mid-depth research on quantum computing"
            }
          ],

          "invocation_target": "agent-research-001:deep_research"
        }
      ],

      "skills": [
        {
          "id": "web_search",
          "description": "Search the web using multiple search engines",
          "tags": ["web", "search", "data"],

          "input_schema": {
            "type": "object",
            "properties": {
              "query": {"type": "string"},
              "num_results": {
                "type": "integer",
                "default": 10,
                "minimum": 1,
                "maximum": 100
              }
            },
            "required": ["query"]
          },

          "invocation_target": "agent-research-001:skill:web_search"
        }
      ]
    }
  ]
}
```

### 3.5 Response Format (XML)

When `?format=xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<discovery discovered_at="2025-11-23T10:30:00Z">
  <summary
    total_agents="5"
    total_reasoners="23"
    total_skills="45"/>

  <capabilities>
    <agent
      id="agent-research-001"
      base_url="http://agent-research:8080"
      version="2.3.1"
      health_status="active"
      deployment_type="long_running"
      last_heartbeat="2025-11-23T10:29:45Z">

      <reasoners>
        <reasoner
          id="deep_research"
          target="agent-research-001:deep_research">
          <description>Performs comprehensive research using multiple sources</description>
          <tags>
            <tag>research</tag>
            <tag>ml</tag>
            <tag>synthesis</tag>
          </tags>
          <input_schema>
            <field name="query" type="string" required="true">
              Research query or topic
            </field>
            <field name="depth" type="integer" min="1" max="5" default="3">
              Research depth level
            </field>
            <field name="sources" type="array">
              Specific sources to search
            </field>
          </input_schema>
          <output_schema>
            <field name="findings" type="array">Research findings</field>
            <field name="confidence" type="number" min="0" max="1">Confidence score</field>
          </output_schema>
        </reasoner>
      </reasoners>

      <skills>
        <skill
          id="web_search"
          target="agent-research-001:skill:web_search">
          <description>Search the web using multiple search engines</description>
          <tags>
            <tag>web</tag>
            <tag>search</tag>
          </tags>
        </skill>
      </skills>
    </agent>
  </capabilities>
</discovery>
```

### 3.6 Response Format (Compact)

When `?format=compact`:

```json
{
  "discovered_at": "2025-11-23T10:30:00Z",
  "reasoners": [
    {
      "id": "deep_research",
      "agent_id": "agent-research-001",
      "target": "agent-research-001:deep_research",
      "tags": ["research", "ml", "synthesis"]
    }
  ],
  "skills": [
    {
      "id": "web_search",
      "agent_id": "agent-research-001",
      "target": "agent-research-001:skill:web_search",
      "tags": ["web", "search", "data"]
    }
  ]
}
```

### 3.7 Error Responses

**400 Bad Request:**
```json
{
  "error": "invalid_parameter",
  "message": "Invalid format parameter. Must be one of: json, xml, compact",
  "details": {
    "parameter": "format",
    "provided": "yaml",
    "allowed": ["json", "xml", "compact"]
  }
}
```

**500 Internal Server Error:**
```json
{
  "error": "internal_error",
  "message": "Failed to retrieve agent capabilities",
  "request_id": "req_abc123"
}
```

---

## 4. Implementation Requirements

### 4.1 Performance Requirements

| Metric              | Target     | Measurement     |
| ------------------- | ---------- | --------------- |
| Response Time (p50) | <50ms      | Without schemas |
| Response Time (p95) | <100ms     | Without schemas |
| Response Time (p99) | <200ms     | With schemas    |
| Throughput          | 1000 req/s | Single instance |
| Cache Hit Rate      | >95%       | 30-second TTL   |
| Memory Usage        | <100MB     | Per instance    |

### 4.2 Scalability Requirements

1. **Horizontal Scaling:** Must support multiple control plane instances
2. **Caching Strategy:**
   - In-memory cache with 30-second TTL
   - Cache invalidation on agent registration/deregistration
   - Read-through cache pattern
3. **Database Queries:**
   - Maximum 1 database query per request (cached)
   - Use existing `ListAgents()` with no additional queries
   - All filtering done in-memory on cached data

### 4.3 Data Sources

**Primary:** `storage.StorageProvider.ListAgents()`
- Returns all active agents with their reasoners and skills
- Already includes health status and metadata
- No schema changes required

**Schema Requirements:**
- Reasoners must have: `ID`, `InputSchema`, `OutputSchema`, `Tags`
- Skills must have: `ID`, `InputSchema`, `Tags`
- All schema fields already exist in `types.AgentNode`

### 4.4 Handler Implementation (Go)

**File:** `control-plane/internal/handlers/discovery.go`

**Key Functions:**
1. `DiscoveryCapabilitiesHandler(storage.StorageProvider) gin.HandlerFunc`
2. `parseDiscoveryFilters(*gin.Context) DiscoveryFilters`
3. `buildDiscoveryResponse([]*types.AgentNode, DiscoveryFilters) DiscoveryResponse`
4. `matchesPattern(value string, pattern string) bool`
5. `matchesFilters(id string, tags []string, filters DiscoveryFilters) bool`
6. `formatJSONResponse(DiscoveryResponse) interface{}`
7. `formatXMLResponse(DiscoveryResponse) string`
8. `formatCompactResponse(DiscoveryResponse) CompactDiscoveryResponse`

**Caching Implementation:**
```go
var (
    agentCache      []*types.AgentNode
    agentCacheLock  sync.RWMutex
    agentCacheTime  time.Time
    agentCacheTTL   = 30 * time.Second
)

func getCachedAgents(ctx context.Context, storage storage.StorageProvider) ([]*types.AgentNode, error) {
    agentCacheLock.RLock()
    if time.Since(agentCacheTime) < agentCacheTTL && agentCache != nil {
        defer agentCacheLock.RUnlock()
        return agentCache, nil
    }
    agentCacheLock.RUnlock()

    agents, err := storage.ListAgents(ctx, types.AgentFilters{})
    if err != nil {
        return nil, err
    }

    agentCacheLock.Lock()
    agentCache = agents
    agentCacheTime = time.Now()
    agentCacheLock.Unlock()

    return agents, nil
}
```

### 4.5 Routing

**Add to:** `control-plane/internal/server/routes.go` (or equivalent)

```go
// Discovery API
discoveryGroup := api.Group("/discovery")
{
    discoveryGroup.GET("/capabilities", handlers.DiscoveryCapabilitiesHandler(storageProvider))
}
```

---

## 5. Testing Requirements

### 5.1 Unit Tests

**File:** `control-plane/internal/handlers/discovery_test.go`

**Test Cases:**
1. ✅ Basic discovery (no filters)
2. ✅ Filter by single agent_id
3. ✅ Filter by multiple agent_ids
4. ✅ Alias support (agent vs node_id)
5. ✅ Wildcard pattern matching (contains, prefix, suffix)
6. ✅ Tag filtering with wildcards
7. ✅ Reasoner filtering
8. ✅ Skill filtering
9. ✅ Schema inclusion flags
10. ✅ JSON format response
11. ✅ XML format response
12. ✅ Compact format response
13. ✅ Pagination (limit/offset)
14. ✅ Health status filtering
15. ✅ Cache hit/miss scenarios
16. ✅ Error handling (invalid format, invalid parameters)

### 5.2 Integration Tests

**File:** `tests/functional/tests/test_discovery_api.py`

**Scenarios:**
1. End-to-end discovery with real agent registration
2. Performance under load (1000 concurrent requests)
3. Cache invalidation on agent updates
4. Large result set pagination


---

## 6. Documentation Requirements

### 6.1 API Documentation

**File:** `docs/api/DISCOVERY_API.md`

**Sections:**
1. Overview and purpose
2. Authentication (if applicable)
3. Endpoint specification
4. Query parameter reference
5. Response format examples (all 3 formats)
6. Error codes and handling
7. Rate limiting (if applicable)
8. Best practices

### 6.2 Developer Guide

**File:** `docs/guides/USING_DISCOVERY_API.md`

**Topics:**
1. Common use cases
2. Example: AI orchestrator pattern
3. Example: Dynamic routing
4. Example: Schema validation
5. Performance optimization tips
6. Troubleshooting

---

## 7. Monitoring & Observability

### 7.1 Metrics

**Prometheus Metrics to Add:**
```
# Request metrics
agentfield_discovery_requests_total{format="json|xml|compact", status="success|error"}
agentfield_discovery_request_duration_seconds{format="json|xml|compact"}

# Cache metrics
agentfield_discovery_cache_hits_total
agentfield_discovery_cache_misses_total
agentfield_discovery_cache_size_bytes

# Filter usage metrics
agentfield_discovery_filter_usage{filter_type="reasoner|skill|tag|agent"}
```

### 7.2 Logging

**Log Events:**
- Discovery request received (DEBUG)
- Cache hit/miss (DEBUG)
- Filter application (DEBUG)
- Response sent (INFO with timing)
- Errors (ERROR with context)

**Log Format:**
```json
{
  "level": "info",
  "timestamp": "2025-11-23T10:30:00Z",
  "message": "discovery request completed",
  "request_id": "req_abc123",
  "filters": {
    "agent_ids": ["agent-1", "agent-2"],
    "reasoner": "*research*",
    "format": "json"
  },
  "results": {
    "agents": 2,
    "reasoners": 5,
    "skills": 10
  },
  "duration_ms": 45,
  "cache_hit": true
}
```

---


---

## 9. Dependencies

### 9.1 Internal Dependencies
- ✅ `storage.StorageProvider.ListAgents()` - Already exists
- ✅ `types.AgentNode` schema - Already exists
- ✅ Gin router framework - Already in use

### 9.2 External Dependencies
- None

---

## 10. Open Questions

1. **Q:** Should we support regex patterns in addition to wildcards?
   **A:** No, wildcards are sufficient for v1. Regex adds complexity.

2. **Q:** Should filter combinations use AND or OR logic?
   **A:** AND logic (all filters must match). OR can be added later if needed.

3. **Q:** Should we support sorting (e.g., by agent_id, version)?
   **A:** Not in v1. Results can be sorted client-side.

4. **Q:** Should we expose internal agent metadata (last_heartbeat, health_score)?
   **A:** Yes, but only health_status and last_heartbeat for now.

---

## 11. Success Metrics

### 11.1 Adoption Metrics
- Number of unique clients using discovery API
- Discovery API requests per day
- Percentage of executions preceded by discovery call

### 11.2 Performance Metrics
- Average response time
- Cache hit rate
- Error rate

### 11.3 Business Metrics
- Number of AI orchestrator implementations built
- Developer satisfaction (via surveys)
- Time to integrate (target: <1 hour)

---

## 12. Python SDK Developer Experience

### 12.1 API Overview

Python developers access discovery through `app.discover()` on the `Agent` class.

### 12.2 Method Signature

```python
from agentfield import Agent

app = Agent()

capabilities = app.discover(
    # Filter by agent (aliases supported)
    agent="agent-001",          # or node_id="agent-001" same wild card support
    agent_ids=["a1", "a2"],     # or node_ids=["a1", "a2"] same wild card support

    # Filter by capability patterns (wildcards supported)
    reasoner="*research*",      # matches: deep_research, web_researcher, etc.
    skill="web_*",              # matches: web_search, web_scraper, etc.
    tags=["ml*", "*learning"],  # matches tags with wildcards

    # Schema options
    include_input_schema=True,
    include_output_schema=True,
    include_descriptions=True,  # default: True
    include_examples=False,

    # Format options
    format="json",  # or "xml", "compact"


    # Pagination
    limit=100,
    offset=0
)
```

### 12.3 Usage Examples

**Basic Discovery:**
```python
from agentfield import Agent

app = Agent()

# Discover all capabilities
capabilities = app.discover()

print(f"Found {capabilities.total_agents} agents")
print(f"Found {capabilities.total_reasoners} reasoners")
print(f"Found {capabilities.total_skills} skills")
```

**Filter by Wildcard Patterns:**
```python
# Find all research-related reasoners
research_caps = app.discover(
    reasoner="*research*",
    include_input_schema=True
)

# Find web skills
web_skills = app.discover(
    skill="web_*",
    tags=["web", "scraping"]
)

# Find ML capabilities (tag wildcards)
ml_caps = app.discover(
    tags=["ml*"],
    health_status="active"
)
```

**Access Discovered Capabilities:**
```python
capabilities = app.discover(
    reasoner="*research*",
    include_input_schema=True
)

# Iterate through discovered agents
for agent_cap in capabilities.capabilities:
    print(f"Agent: {agent_cap.agent_id}")

    # Access reasoners
    for reasoner in agent_cap.reasoners:
        print(f"  Reasoner: {reasoner.id}")
        print(f"  Target: {reasoner.invocation_target}")
        print(f"  Tags: {reasoner.tags}")
        print(f"  Input Schema: {reasoner.input_schema}")
```

**Use with app.execute():**
```python
# Discover capabilities
capabilities = app.discover(
    tags=["research"],
    include_input_schema=True
)

# Select a reasoner
reasoner = capabilities.capabilities[0].reasoners[0]

# Execute using the discovered target
result = app.execute(
    target=reasoner.invocation_target,
    input={"query": "AI trends 2025"}
)
```

**XML Format for LLM Context:**
```python
# Get capabilities in XML format for LLM context
xml_capabilities = app.discover(
    format="xml",
    include_descriptions=True
)

# Use in LLM system prompt
system_prompt = f"""
You have access to these capabilities:

{xml_capabilities}

Select and use the appropriate capability for the user's request.
"""
```

**Compact Format:**
```python
# Get lightweight capability list
compact_caps = app.discover(format="compact")

# Compact format returns minimal data:
# {
#   "reasoners": [{"id": "...", "agent_id": "...", "target": "...", "tags": [...]}],
#   "skills": [{"id": "...", "agent_id": "...", "target": "...", "tags": [...]}]
# }
```

### 12.4 Response Object Structure

```python
# Response type
class DiscoveryResponse:
    discovered_at: datetime
    total_agents: int
    total_reasoners: int
    total_skills: int
    pagination: Pagination
    capabilities: List[AgentCapability]

class AgentCapability:
    agent_id: str
    base_url: str
    version: str
    health_status: str
    deployment_type: str
    last_heartbeat: datetime
    reasoners: List[ReasonerCapability]
    skills: List[SkillCapability]

class ReasonerCapability:
    id: str
    description: Optional[str]
    tags: List[str]
    input_schema: Optional[dict]
    output_schema: Optional[dict]
    examples: Optional[List[dict]]
    invocation_target: str

class SkillCapability:
    id: str
    description: Optional[str]
    tags: List[str]
    input_schema: Optional[dict]
    invocation_target: str
```

---

## 13. Go SDK Developer Experience

### 13.1 API Overview

Go developers access discovery through the `Discover()` method with functional options pattern.

### 13.2 Method Signature

```go
import (
    "context"
    "github.com/Agent-Field/agentfield/sdk/go/agent"
)

app := agent.NewAgent()

// Discover with options
capabilities, err := app.Discover(
    context.Background(),

    // Filter by agent (aliases supported)
    agent.WithAgent("agent-001"),            // or WithNodeID("agent-001")
    agent.WithAgentIDs([]string{"a1", "a2"}), // or WithNodeIDs(...)

    // Filter by capability patterns (wildcards supported)
    agent.WithReasonerPattern("*research*"),
    agent.WithSkillPattern("web_*"),
    agent.WithTags([]string{"ml*", "*learning"}),

    // Schema options
    agent.WithInputSchema(true),
    agent.WithOutputSchema(true),
    agent.WithDescriptions(true),  // default: true
    agent.WithExamples(false),

    // Format options
    agent.WithFormat("json"),  // or "xml", "compact"

    // Health filtering
    agent.WithHealthStatus("active"),

    // Pagination
    agent.WithLimit(100),
    agent.WithOffset(0),
)
```

### 13.3 Usage Examples

**Basic Discovery:**
```go
package main

import (
    "context"
    "fmt"
    "github.com/Agent-Field/agentfield/sdk/go/agent"
)

func main() {
    app := agent.NewAgent()
    ctx := context.Background()

    // Discover all capabilities
    capabilities, err := app.Discover(ctx)
    if err != nil {
        panic(err)
    }

    fmt.Printf("Found %d agents\n", capabilities.TotalAgents)
    fmt.Printf("Found %d reasoners\n", capabilities.TotalReasoners)
    fmt.Printf("Found %d skills\n", capabilities.TotalSkills)
}
```

**Filter by Wildcard Patterns:**
```go
// Find research-related reasoners
researchCaps, err := app.Discover(
    ctx,
    agent.WithReasonerPattern("*research*"),
    agent.WithInputSchema(true),
)

// Find web skills
webSkills, err := app.Discover(
    ctx,
    agent.WithSkillPattern("web_*"),
    agent.WithTags([]string{"web", "scraping"}),
)

// Find ML capabilities (tag wildcards)
mlCaps, err := app.Discover(
    ctx,
    agent.WithTags([]string{"ml*"}),
    agent.WithHealthStatus("active"),
)
```

**Access Discovered Capabilities:**
```go
capabilities, err := app.Discover(
    ctx,
    agent.WithReasonerPattern("*research*"),
    agent.WithInputSchema(true),
)
if err != nil {
    panic(err)
}

// Iterate through discovered agents
for _, agentCap := range capabilities.Capabilities {
    fmt.Printf("Agent: %s\n", agentCap.AgentID)

    // Access reasoners
    for _, reasoner := range agentCap.Reasoners {
        fmt.Printf("  Reasoner: %s\n", reasoner.ID)
        fmt.Printf("  Target: %s\n", reasoner.InvocationTarget)
        fmt.Printf("  Tags: %v\n", reasoner.Tags)
        fmt.Printf("  Input Schema: %+v\n", reasoner.InputSchema)
    }
}
```

**Use with app.Execute():**
```go
// Discover capabilities
capabilities, err := app.Discover(
    ctx,
    agent.WithTags([]string{"research"}),
    agent.WithInputSchema(true),
)
if err != nil {
    panic(err)
}

// Select a reasoner
reasoner := capabilities.Capabilities[0].Reasoners[0]

// Execute using the discovered target
result, err := app.Execute(ctx, agent.ExecuteRequest{
    Target: reasoner.InvocationTarget,
    Input: map[string]interface{}{
        "query": "AI trends 2025",
    },
})
```

**XML Format for LLM Context:**
```go
// Get capabilities in XML format
xmlCaps, err := app.Discover(
    ctx,
    agent.WithFormat("xml"),
    agent.WithDescriptions(true),
)
if err != nil {
    panic(err)
}

// Use in LLM system prompt
systemPrompt := fmt.Sprintf(`
You have access to these capabilities:

%s

Select and use the appropriate capability for the user's request.
`, xmlCaps)
```

**Compact Format:**
```go
// Get lightweight capability list
compactCaps, err := app.Discover(
    ctx,
    agent.WithFormat("compact"),
)

// Compact format returns minimal data
```

### 13.4 Response Types

```go
type DiscoveryResponse struct {
    DiscoveredAt   time.Time          `json:"discovered_at"`
    TotalAgents    int                `json:"total_agents"`
    TotalReasoners int                `json:"total_reasoners"`
    TotalSkills    int                `json:"total_skills"`
    Pagination     Pagination         `json:"pagination"`
    Capabilities   []AgentCapability  `json:"capabilities"`
}

type AgentCapability struct {
    AgentID        string              `json:"agent_id"`
    BaseURL        string              `json:"base_url"`
    Version        string              `json:"version"`
    HealthStatus   string              `json:"health_status"`
    DeploymentType string              `json:"deployment_type"`
    LastHeartbeat  time.Time           `json:"last_heartbeat"`
    Reasoners      []ReasonerCapability `json:"reasoners"`
    Skills         []SkillCapability    `json:"skills"`
}

type ReasonerCapability struct {
    ID               string                 `json:"id"`
    Description      *string                `json:"description,omitempty"`
    Tags             []string               `json:"tags"`
    InputSchema      map[string]interface{} `json:"input_schema,omitempty"`
    OutputSchema     map[string]interface{} `json:"output_schema,omitempty"`
    Examples         []map[string]interface{} `json:"examples,omitempty"`
    InvocationTarget string                 `json:"invocation_target"`
}

type SkillCapability struct {
    ID               string                 `json:"id"`
    Description      *string                `json:"description,omitempty"`
    Tags             []string               `json:"tags"`
    InputSchema      map[string]interface{} `json:"input_schema,omitempty"`
    InvocationTarget string                 `json:"invocation_target"`
}
```

---

## 14. Appendix

### 12.1 Example Use Cases

**Use Case 1: AI Orchestrator**
```python
# AI discovers and selects appropriate reasoner
capabilities = app.discover(
    tags=["research"],
    include_input_schema=True
)

# AI selects best match and executes
selected = ai_select_best_reasoner(capabilities, user_query)
result = app.execute(target=selected.invocation_target, input=user_input)
```

**Use Case 2: Dynamic Tool Registry**
```python
# Build tool registry for LLM
tools = app.discover(
    format="compact",
    include_descriptions=True
)

# Pass to LLM for tool use
llm_response = openai.chat.completions.create(
    model="gpt-4",
    messages=[...],
    tools=convert_to_openai_tools(tools)
)
```

**Use Case 3: Health Monitoring**
```python
# Monitor available capabilities
healthy_agents = app.discover(
    health_status="active",
    include_input_schema=False
)

alert_if_below_threshold(len(healthy_agents.capabilities), min_agents=3)
```

### 12.2 References
- AgentField Architecture: `docs/ARCHITECTURE.md`
- Agent Registration API: `docs/api/AGENT_REGISTRATION.md`
- Execution API: `docs/api/EXECUTION_API.md`

---

Perfect! Let me redesign this with a much simpler, focused approach that's integrated into the existing `app` object and optimized for AI orchestrators making just-in-time decisions.

---

## 🎯 **Refined Vision: Simple Discovery for AI Orchestration**

Core use case: **AI orchestrator needs to discover available reasoners/skills and their schemas to make intelligent routing decisions at runtime.**

---

## 🏗️ **Simplified API Design**

### **Single Discovery Endpoint**

```
GET /api/v1/discovery/capabilities
```

**Query Parameters:**

```yaml
# Agent/Node Filtering
?agent_id=agent-research-001    # Specific agent (node_id = agent_id)
?agent_ids=agent-1,agent-2      # Multiple agents

# Capability Filtering with Wildcards
?reasoner=*research*            # Wildcard matching
?reasoner=deep_*                # Prefix matching
?skill=web_*                    # Skill wildcard
?tags=ml,nlp                    # Exact tag match
?tags=ml*,*research             # Tag wildcards

# Schema Control
?include_input_schema=true      # Include input schemas (default: false)
?include_output_schema=true     # Include output schemas (default: false)
?include_descriptions=true      # Include descriptions (default: true)
?include_examples=false         # Include usage examples (default: false)

# Format Options
?format=json                    # json | xml | compact
# - json: Full JSON response
# - xml: XML for easy LLM context injection
# - compact: Minimal response, just IDs and names

# Pagination
?limit=100
?offset=0
```

---

### **Response Structure (JSON)**

```json
{
  "discovered_at": "2025-11-23T10:30:00Z",
  "total_agents": 5,
  "total_reasoners": 23,
  "total_skills": 45,

  "capabilities": [
    {
      "agent_id": "agent-research-001",
      "base_url": "http://agent-research:8080",
      "version": "2.3.1",
      "health_status": "active",

      "reasoners": [
        {
          "id": "deep_research",
          "description": "Performs comprehensive research using multiple sources",
          "tags": ["research", "ml", "synthesis"],

          "input_schema": {
            "type": "object",
            "properties": {
              "query": {"type": "string", "description": "Research query"},
              "depth": {"type": "integer", "min": 1, "max": 5, "default": 3}
            },
            "required": ["query"]
          },

          "output_schema": {
            "type": "object",
            "properties": {
              "findings": {"type": "array"},
              "confidence": {"type": "number"}
            }
          },

          "examples": [
            {
              "input": {"query": "quantum computing advances"},
              "description": "Basic research query"
            }
          ],

          "invocation_target": "agent-research-001:deep_research"
        }
      ],

      "skills": [
        {
          "id": "web_search",
          "description": "Search the web",
          "tags": ["web", "search"],

          "input_schema": {
            "type": "object",
            "properties": {
              "query": {"type": "string"},
              "num_results": {"type": "integer", "default": 10}
            }
          },

          "invocation_target": "agent-research-001:skill:web_search"
        }
      ]
    }
  ]
}
```

---

### **XML Format (for LLM Context)**

When `?format=xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<capabilities discovered_at="2025-11-23T10:30:00Z">
  <summary total_agents="5" total_reasoners="23" total_skills="45"/>

  <agent id="agent-research-001" base_url="http://agent-research:8080" health_status="active">
    <reasoners>
      <reasoner id="deep_research" target="agent-research-001:deep_research">
        <description>Performs comprehensive research using multiple sources</description>
        <tags>
          <tag>research</tag>
          <tag>ml</tag>
          <tag>synthesis</tag>
        </tags>
        <input_schema>
          <field name="query" type="string" required="true">Research query</field>
          <field name="depth" type="integer" min="1" max="5" default="3">Research depth</field>
        </input_schema>
        <output_schema>
          <field name="findings" type="array">Research findings</field>
          <field name="confidence" type="number">Confidence score</field>
        </output_schema>
      </reasoner>
    </reasoners>

    <skills>
      <skill id="web_search" target="agent-research-001:skill:web_search">
        <description>Search the web</description>
        <tags>
          <tag>web</tag>
          <tag>search</tag>
        </tags>
      </skill>
    </skills>
  </agent>
</capabilities>
```

---

### **Compact Format**

When `?format=compact`:

```json
{
  "reasoners": [
    {
      "id": "deep_research",
      "agent_id": "agent-research-001",
      "target": "agent-research-001:deep_research",
      "tags": ["research", "ml"]
    }
  ],
  "skills": [
    {
      "id": "web_search",
      "agent_id": "agent-research-001",
      "target": "agent-research-001:skill:web_search",
      "tags": ["web", "search"]
    }
  ]
}
```

---

## 🐍 **Python SDK Integration (`app.discover()`)**

```python
from agentfield import Agent

app = Agent()

# Simple discovery - get all capabilities
capabilities = app.discover()

# Filter by reasoner pattern (wildcard)
research_reasoners = app.discover(
    reasoner="*research*",
    include_input_schema=True
)

# Filter by tags (with wildcards)
ml_capabilities = app.discover(
    tags=["ml*", "*learning"],
    include_input_schema=True,
    include_output_schema=True
)

# Get specific agent's capabilities
agent_caps = app.discover(
    agent_id="agent-research-001"
)

# Get in XML format for LLM context
xml_manifest = app.discover(
    format="xml",
    include_descriptions=True
)

# Compact format for quick lookup
targets = app.discover(format="compact")

# Example: AI orchestrator selecting a reasoner
def route_to_best_reasoner(user_query: str):
    # Discover all research-related reasoners
    researchers = app.discover(
        tags=["research"],
        include_input_schema=True
    )

    # AI logic to select best match
    for cap in researchers.capabilities:
        for reasoner in cap.reasoners:
            if matches_requirements(reasoner.input_schema, user_query):
                # Execute the selected reasoner
                result = app.execute(
                    target=reasoner.invocation_target,
                    input={"query": user_query}
                )
                return result
```

---

## 🔧 **Go SDK Integration**

```go
package main

import (
    "github.com/Agent-Field/agentfield/sdk/go/agent"
)

func main() {
    app := agent.NewAgent()

    // Simple discovery
    caps, err := app.Discover()

    // Filter by reasoner pattern
    researchReasoners, err := app.Discover(
        agent.WithReasonerPattern("*research*"),
        agent.WithInputSchema(true),
    )

    // Filter by tags with wildcards
    mlCaps, err := app.Discover(
        agent.WithTags([]string{"ml*", "*learning"}),
        agent.WithSchemas(true),
    )

    // Get XML format
    xmlManifest, err := app.Discover(
        agent.WithFormat("xml"),
    )

    // Example: AI orchestrator
    func routeToBestReasoner(userQuery string) {
        caps, _ := app.Discover(
            agent.WithTags([]string{"research"}),
            agent.WithInputSchema(true),
        )

        for _, agentCap := range caps.Capabilities {
            for _, reasoner := range agentCap.Reasoners {
                if matchesRequirements(reasoner.InputSchema, userQuery) {
                    result, _ := app.Execute(agent.ExecuteRequest{
                        Target: reasoner.InvocationTarget,
                        Input:  map[string]interface{}{"query": userQuery},
                    })
                    return result
                }
            }
        }
    }
}
```

---

## ⚡ **Control Plane Implementation (Scalable)**

### **Handler Function**

```go
// control-plane/internal/handlers/discovery.go

func DiscoveryCapabilitiesHandler(storageProvider storage.StorageProvider) gin.HandlerFunc {
    return func(c *gin.Context) {
        // Parse query parameters
        filters := parseDiscoveryFilters(c)

        // Get agents from storage (already cached/indexed)
        agents, err := storageProvider.ListAgents(c.Request.Context(), types.AgentFilters{
            // Health filtering optional
        })

        if err != nil {
            c.JSON(500, gin.H{"error": "failed to fetch agents"})
            return
        }

        // Filter and build response in-memory (fast)
        response := buildDiscoveryResponse(agents, filters)

        // Return in requested format
        switch filters.Format {
        case "xml":
            c.XML(200, response.ToXML())
        case "compact":
            c.JSON(200, response.ToCompact())
        default:
            c.JSON(200, response)
        }
    }
}

// In-memory filtering (no DB queries per filter)
func buildDiscoveryResponse(agents []*types.AgentNode, filters DiscoveryFilters) DiscoveryResponse {
    response := DiscoveryResponse{
        DiscoveredAt: time.Now(),
    }

    for _, agent := range agents {
        // Apply agent_id filter
        if filters.AgentID != nil && agent.ID != *filters.AgentID {
            continue
        }

        agentCap := AgentCapability{
            AgentID:      agent.ID,
            BaseURL:      agent.BaseURL,
            Version:      agent.Version,
            HealthStatus: string(agent.HealthStatus),
        }

        // Filter reasoners
        for _, reasoner := range agent.Reasoners {
            if matchesFilters(reasoner.ID, reasoner.Tags, filters) {
                agentCap.Reasoners = append(agentCap.Reasoners, buildReasonerResponse(reasoner, agent.ID, filters))
            }
        }

        // Filter skills
        for _, skill := range agent.Skills {
            if matchesFilters(skill.ID, skill.Tags, filters) {
                agentCap.Skills = append(agentCap.Skills, buildSkillResponse(skill, agent.ID, filters))
            }
        }

        if len(agentCap.Reasoners) > 0 || len(agentCap.Skills) > 0 {
            response.Capabilities = append(response.Capabilities, agentCap)
        }
    }

    return response
}

// Wildcard matching
func matchesPattern(value string, pattern string) bool {
    if !strings.Contains(pattern, "*") {
        return value == pattern
    }

    // Simple wildcard matching
    if strings.HasPrefix(pattern, "*") && strings.HasSuffix(pattern, "*") {
        // *abc* - contains
        return strings.Contains(value, strings.Trim(pattern, "*"))
    } else if strings.HasPrefix(pattern, "*") {
        // *abc - ends with
        return strings.HasSuffix(value, strings.TrimPrefix(pattern, "*"))
    } else if strings.HasSuffix(pattern, "*") {
        // abc* - starts with
        return strings.HasPrefix(value, strings.TrimSuffix(pattern, "*"))
    }

    return value == pattern
}

func matchesFilters(id string, tags []string, filters DiscoveryFilters) bool {
    // Check reasoner/skill pattern
    if filters.ReasonerPattern != nil && !matchesPattern(id, *filters.ReasonerPattern) {
        return false
    }
    if filters.SkillPattern != nil && !matchesPattern(id, *filters.SkillPattern) {
        return false
    }

    // Check tags (with wildcard support)
    if len(filters.Tags) > 0 {
        matched := false
        for _, filterTag := range filters.Tags {
            for _, tag := range tags {
                if matchesPattern(tag, filterTag) {
                    matched = true
                    break
                }
            }
            if matched {
                break
            }
        }
        if !matched {
            return false
        }
    }

    return true
}
```

---

## 🎯 **Key Features for AI Orchestrators**

### **1. Schema-Based Routing**

```python
# AI orchestrator discovers and routes based on input requirements
def intelligent_route(user_input: dict):
    # Discover capabilities with schemas
    caps = app.discover(
        include_input_schema=True,
        include_output_schema=True
    )

    # Find reasoners that can handle this input structure
    for cap in caps.capabilities:
        for reasoner in cap.reasoners:
            if validates_against_schema(user_input, reasoner.input_schema):
                return app.execute(
                    target=reasoner.invocation_target,
                    input=user_input
                )
```

### **2. Tag-Based Discovery**

```python
# Find all ML-related capabilities
ml_tools = app.discover(tags=["ml*"])

# Find web scraping tools
web_tools = app.discover(tags=["web", "scraping"])
```

### **3. Just-In-Time Tool Selection**

```python
# AI decides at runtime which tool to use
def ai_orchestrator(task_description: str):
    # Get all available tools in compact format
    tools = app.discover(format="compact")

    # AI analyzes task and selects appropriate tool
    selected_tool = ai_model.select_tool(task_description, tools)

    # Execute selected tool
    result = app.execute(target=selected_tool.target, input={...})
```

---

## 📊 **Performance Considerations**

### **Caching Strategy**

```go
// Cache agent list with 30s TTL
var (
    agentCache      []*types.AgentNode
    agentCacheLock  sync.RWMutex
    agentCacheTime  time.Time
    cacheTTL        = 30 * time.Second
)

func getCachedAgents(ctx context.Context, storage storage.StorageProvider) ([]*types.AgentNode, error) {
    agentCacheLock.RLock()
    if time.Since(agentCacheTime) < cacheTTL && agentCache != nil {
        defer agentCacheLock.RUnlock()
        return agentCache, nil
    }
    agentCacheLock.RUnlock()

    // Refresh cache
    agents, err := storage.ListAgents(ctx, types.AgentFilters{})
    if err != nil {
        return nil, err
    }

    agentCacheLock.Lock()
    agentCache = agents
    agentCacheTime = time.Now()
    agentCacheLock.Unlock()

    return agents, nil
}
```

---

## 🚀 **Example: AI Orchestrator Use Case**

```python
from agentfield import Agent
import openai

app = Agent()

def ai_orchestrated_task(user_request: str):
    """
    AI orchestrator that discovers capabilities and routes intelligently
    """

    # Step 1: Discover available tools
    available_tools = app.discover(
        include_input_schema=True,
        include_descriptions=True,
        format="json"
    )

    # Step 2: Convert to LLM-friendly format
    tool_descriptions = []
    for cap in available_tools.capabilities:
        for reasoner in cap.reasoners:
            tool_descriptions.append({
                "name": reasoner.id,
                "description": reasoner.description,
                "target": reasoner.invocation_target,
                "parameters": reasoner.input_schema
            })

    # Step 3: Let AI select the right tool
    ai_response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": f"Available tools: {tool_descriptions}"},
            {"role": "user", "content": user_request}
        ],
        tools=[{"type": "function", "function": t} for t in tool_descriptions]
    )

    # Step 4: Execute selected tool
    if ai_response.tool_calls:
        tool_call = ai_response.tool_calls[0]
        result = app.execute(
            target=get_target_from_tool_name(tool_call.name, tool_descriptions),
            input=json.loads(tool_call.arguments)
        )
        return result
```

---

## ✅ **Simplified Feature Set**

**Core Features:**
- ✅ Wildcard filtering (reasoners, skills, tags)
- ✅ Schema inclusion options
- ✅ Multiple output formats (JSON, XML, Compact)
- ✅ Integrated into `app` object
- ✅ Efficient caching for scalability
- ✅ Perfect for AI orchestrators

**Not Included (for now):**
- ❌ Semantic search
- ❌ Performance metrics
- ❌ Team ID filtering
- ❌ MCP integration
- ❌ Natural language queries
- ❌ WebSocket streaming

---
