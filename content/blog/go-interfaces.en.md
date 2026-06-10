---
title: "Go interfaces: small is beautiful"
date: 2026-04-10
description: "The one-method interface is Go's most underrated feature. It's not a constraint — it's the whole philosophy in a single concept."
draft: false
---

If you come from Java or C#, your instinct is to design big interfaces and have types implement them. Go inverts this completely.

## Accept interfaces, return structs

This single rule — if you follow nothing else — will make your Go code significantly easier to test and extend.

```go
// Bad: accepting a concrete type
func Process(db *PostgresDB) error { ... }

// Good: accepting an interface
type Store interface {
    Get(id string) (Record, error)
}
func Process(s Store) error { ... }
```

The interface lives at the point of use, not at the point of definition. That's the inversion.
