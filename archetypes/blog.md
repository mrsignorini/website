---
title: "{{ replace .File.ContentBaseName "-" " " | title }}"
date: {{ .Date }}
description: ""
draft: true
---

Brief hook — one or two sentences framing the problem or tension this post addresses.

## The problem

What breaks, frustrates, or is misunderstood without the knowledge in this post.

## What [topic] is

Definition, mental model, ASCII or Mermaid diagram if applicable.

### System context

```mermaid
C4Context
  title System Context — [Topic]
  ...
```

### Request flow (optional)

```mermaid
sequenceDiagram
  ...
```

## [Core concept 1]

## [Core concept 2]

## History and adoption timeline (optional)

- **[Date]** — ...

## What makes a good [topic] (optional)

Numbered list of design principles.

## Where it goes from here

Forward-looking paragraph. One or two frontiers.

---

## Further reading

- [Title](URL) — one-line description
- [Title](URL) — one-line description

---

## About the author

**Ivens Signorini** is a Senior Backend Engineer focused on distributed systems, AI infrastructure, and high-performance APIs. He works primarily in Go and TypeScript, building systems that run at scale. His technical interests include protocol design, concurrency patterns, and the architecture of AI-native applications. He writes at [signorini.cloud](https://signorini.cloud).
