---
title: "What distributed systems taught me about trade-offs"
date: 2026-05-20
description: "Consistency, availability, partition tolerance — pick two. But the real lesson is that every system has a personality, and yours is defined by which failures you accept."
draft: false
---

Every distributed system is a negotiation. You're not building a machine that always works — you're deciding, deliberately, how it fails.

## The CAP theorem is misunderstood

Most engineers treat CAP as a menu: pick two. But that framing is too static. Real systems don't sit at a fixed point in that triangle — they shift depending on what's failing and what the client is asking for.

## Failure is the spec

The insight that changed how I design systems: **failure modes are first-class requirements**. If you don't write them down, you'll discover them in production.

Write the failure doc before the happy-path doc. It forces better questions.
