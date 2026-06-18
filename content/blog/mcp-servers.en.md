---
title: "MCP Servers: the protocol that gave AI hands"
date: 2026-06-17
description: "What is the Model Context Protocol, where it came from, and why every serious AI integration now speaks it."
draft: false
---

AI models are extraordinary at reasoning. They're terrible at acting — or at least they were, until they had a standardized way to reach outside themselves. MCP is that way.

## The problem before MCP

In 2023, if you wanted an LLM to read a file, query a database, or call an API, you wrote custom glue code. Every team reinvented the same wheel: a thin layer that serialized context, passed it to the model, parsed tool calls out of the response, executed them, and fed results back. There was no standard. Every integration was a one-off.

The result was a fragmented ecosystem. Models couldn't reuse tooling across products. Developers couldn't share adapters. Security boundaries were inconsistent. And the complexity scaled with every new tool added.

## What MCP is

**MCP — Model Context Protocol** — is an open protocol published by Anthropic in November 2024. It defines a standard communication interface between AI models (clients) and external services (servers).

The mental model is simple: MCP servers are plugins. They expose **resources** (data the model can read), **tools** (actions the model can invoke), and **prompts** (reusable instruction templates). The model is always the client; the server is always the capability provider.

### System context

```mermaid
C4Context
  title System Context — Model Context Protocol

  Person(developer, "Developer", "Builds and configures MCP servers and clients")

  System_Boundary(mcpBoundary, "MCP Ecosystem") {
    System(aiClient, "AI Client", "LLM host application — Claude Desktop, IDE, custom agent")
    System(mcpServer, "MCP Server", "Capability provider — exposes tools, resources, and prompts via JSON-RPC 2.0")
  }

  System_Ext(filesystem, "Filesystem", "Local or remote files and directories")
  System_Ext(github, "GitHub", "Repositories, PRs, issues, code search")
  System_Ext(database, "Database", "PostgreSQL, SQLite, or any structured store")
  System_Ext(webapis, "External APIs", "Slack, Notion, web search, and other services")

  Rel(developer, aiClient, "Configures and uses")
  Rel(developer, mcpServer, "Implements and deploys")
  Rel(aiClient, mcpServer, "Invokes tools and fetches resources", "JSON-RPC 2.0 / stdio · HTTP+SSE · WebSocket")
  Rel(mcpServer, filesystem, "Reads and writes")
  Rel(mcpServer, github, "Queries and manages")
  Rel(mcpServer, database, "Reads and writes", "SQL / driver")
  Rel(mcpServer, webapis, "Calls", "HTTPS")

  UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

### Request flow

```mermaid
C4Dynamic
  title Dynamic — MCP Tool Invocation Flow

  System(aiClient, "AI Client", "LLM host — Claude, agent, IDE")

  System_Boundary(mcpBoundary, "MCP Server") {
    System(dispatcher, "Request Dispatcher", "Routes JSON-RPC calls to handlers")
    System(toolRegistry, "Tool Registry", "Declares available tools and their schemas")
    System(executor, "Tool Executor", "Runs tool logic and enforces authorization")
  }

  System_Ext(extService, "External Service", "Filesystem, GitHub, DB, API...")

  Rel(aiClient, dispatcher, "1. initialize — negotiate capabilities", "JSON-RPC 2.0")
  Rel(dispatcher, toolRegistry, "2. tools/list — enumerate available tools")
  Rel(toolRegistry, dispatcher, "3. Return tool schemas")
  Rel(dispatcher, aiClient, "4. Capability manifest")
  Rel(aiClient, dispatcher, "5. tools/call — invoke tool with args", "JSON-RPC 2.0")
  Rel(dispatcher, executor, "6. Dispatch to handler")
  Rel(executor, extService, "7. Execute against external service")
  Rel(extService, executor, "8. Return result")
  Rel(executor, dispatcher, "9. Structured result or error")
  Rel(dispatcher, aiClient, "10. JSON-RPC response")
```

The wire protocol is **JSON-RPC 2.0**, running over stdio, HTTP+SSE, or WebSocket depending on deployment context. This is deliberately boring: it means any language can implement it, any infra can host it, and any model can speak it.

## Protocol sequence

The full lifecycle of an MCP session — from handshake to tool result:

```mermaid
sequenceDiagram
    participant C as AI Client
    participant S as MCP Server
    participant E as External Service

    Note over C,S: 1. Connection & Capability Negotiation
    C->>S: initialize {protocolVersion, clientInfo, capabilities}
    S-->>C: {serverInfo, capabilities: {tools, resources, prompts}}

    Note over C,S: 2. Discovery
    C->>S: tools/list
    S-->>C: [{name, description, inputSchema}, ...]
    C->>S: resources/list
    S-->>C: [{uri, name, mimeType}, ...]

    Note over C,S: 3. Resource Fetch (read-only context)
    C->>S: resources/read {uri}
    S-->>C: {contents: [{text | blob}]}

    Note over C,S: 4. Tool Invocation (agent action)
    C->>S: tools/call {name, arguments}
    S->>E: Execute against external service
    E-->>S: Raw result
    S-->>C: {content: [{type, text}], isError: false}

    Note over C,S: 5. Streaming (long-running tools)
    C->>S: tools/call {name, arguments}
    S-->>C: notifications/progress {partial result}
    S-->>C: notifications/progress {partial result}
    S-->>C: {content: [{type, text}], isError: false}
```

## Protocol anatomy

An MCP server exposes three primitive types:

**Resources** — read-only context. A resource could be a file, a database row, a Slack message, a GitHub PR. The server declares what it has; the model decides what to fetch.

**Tools** — callable actions with typed schemas. When a model decides to invoke a tool, it sends a structured JSON call. The server executes it and returns a result. Tools are what make models agents — they turn reasoning into effect.

**Prompts** — parameterized instruction templates. Think of them as server-defined slash commands: reusable patterns the client can invoke with arguments.

All three are declared through a capability negotiation handshake at connection time. The model always knows exactly what a server offers before it tries to use anything.

## Why AI systems adopted it

The adoption argument is straightforward: **one integration, many clients**.

Before MCP, if you built a filesystem adapter for Claude, it worked for Claude. Porting it to another model meant rewriting the interface layer. With MCP, you write the server once. Any MCP-compatible client can use it.

For AI system builders, this is significant. It means:

- **Tool libraries are reusable** across models and products
- **Security is enforced at the server boundary**, not scattered across prompt templates
- **Capability discovery is automatic** — the model negotiates what's available at runtime
- **Streaming is native** — long-running tools can push partial results without polling

The ecosystem effect compounds quickly. Once a GitHub MCP server exists, every model that speaks MCP gets GitHub integration for free. Once a Postgres server exists, every product built on MCP gets structured query access without custom work.

## History and adoption timeline

- **November 2024** — Anthropic publishes MCP specification and open-sources reference implementations in Python and TypeScript. Claude Desktop ships as the first MCP client.
- **Early 2025** — Community MCP server catalog grows past 1,000 implementations. Major integrations: GitHub, Slack, Notion, filesystem, Docker, web search.
- **Mid 2025** — OpenAI, Google DeepMind, and several open-source model providers announce MCP support. The protocol moves from Anthropic-specific to effectively industry standard.
- **Late 2025** — Enterprise tooling vendors (Atlassian, Linear, Salesforce) ship first-party MCP servers. IDE vendors embed MCP clients natively.
- **2026** — MCP is the assumed integration layer for any serious AI product. Not speaking it is now the exception.

The speed of adoption tracks the speed at which developers realized the alternative — custom glue code forever — was not sustainable.

## What makes a good MCP server

Not all servers are equal. A well-designed MCP server:

1. **Keeps tools focused** — one tool, one purpose. A search tool should not also write.
2. **Returns structured output** — typed JSON, not free text, so the model can reason over results reliably.
3. **Fails loudly** — errors returned as proper error objects, not buried in result strings.
4. **Respects authorization** — the server, not the model, decides what the caller is allowed to do.
5. **Is stateless where possible** — context should live in resources, not in server memory.

These are the same principles that make any good API. MCP doesn't change software design — it just applies it at the AI integration layer.

## Where it goes from here

The interesting frontier is **multi-server orchestration**: a single model session connecting to dozens of MCP servers simultaneously, combining capabilities dynamically. Think of a coding agent with simultaneous access to your codebase, GitHub, your issue tracker, your CI logs, and your documentation — all through a single protocol.

The other frontier is **server-to-server composition**: MCP servers that themselves call other MCP servers, building capability graphs rather than flat tool lists.

MCP didn't invent the idea of AI tool use. It standardized it. And in software, standardization is usually where the real leverage lives.

---

## Further reading

- [MCP Official Specification](https://modelcontextprotocol.io/specification) — Anthropic's canonical protocol reference
- [MCP GitHub Repository](https://github.com/modelcontextprotocol) — reference implementations in Python and TypeScript
- [Introducing the Model Context Protocol](https://www.anthropic.com/news/model-context-protocol) — Anthropic's original announcement post
- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification) — the wire protocol MCP runs on
- [awesome-mcp-servers](https://github.com/punkpeye/awesome-mcp-servers) — community-curated list of MCP server implementations

---

## About the author

**Ivens Signorini** is a Senior Backend Engineer focused on distributed systems, AI infrastructure, and high-performance APIs. He works primarily in Go and TypeScript, building systems that run at scale. His technical interests include protocol design, concurrency patterns, and the architecture of AI-native applications. He writes at [signorini.cloud](https://signorini.cloud).
