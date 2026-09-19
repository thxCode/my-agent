---
name: api-and-interface-design
description: Design a stable interface; contract before implementation, errors that mean one thing, change by addition.
---

# API and interface design

Distilled from [`api-and-interface-design`](https://github.com/addyosmani/agent-skills/tree/main/skills/api-and-interface-design)
(MIT, Copyright (c) 2025 Addy Osmani); see `CREDITS.md`.

Read when a task in `my-build` creates or changes something another module, service, or team calls. The
premise: an interface is a promise whose cost lands later, on someone who cannot renegotiate it.

## Hyrum's Law sets the real surface

With enough callers, every observable behaviour of your interface becomes something someone depends on —
field order, an incidental error string, how fast it returns, what it does with an empty list. The contract
is not what you documented; it is what you exposed.

So decide deliberately what to expose, and keep the rest genuinely unobservable. An internal that leaks into
a response is a commitment you did not mean to make.

## Write the contract before the implementation

Name the operations, their inputs, their outputs, and their failure modes *first*, then build to it. Working
backwards from an implementation produces an interface shaped like your current internals — which is exactly
the shape you will want to change first.

The contract has to state what happens at the edges: empty input, absent optional field, the same request
arriving twice, a downstream dependency being unavailable. An edge the contract does not name is an edge
every caller will guess about differently.

## Errors carry one meaning each

A caller distinguishes failures by a stable, machine-readable code — not by matching on prose. Each code
means exactly one thing, and its meaning never widens later: reusing a code for a second condition silently
breaks every caller that branched on the first.

Separate the three kinds, because callers handle them differently: the caller sent something invalid (fix
the request), the caller is not permitted (fix the credentials), the service failed (retry may help). A
single generic failure collapses all three into "try again and hope".

## Validate at the boundary, then trust inward

Parse and validate every external input once, where it enters, and convert it into a type that can only hold
valid values. Internal code that re-checks what the boundary guaranteed is duplicated logic that will drift;
internal code that *should* have re-checked and did not is the vulnerability.

Give a domain concept its own type rather than passing a bare string or number. An identifier that cannot be
swapped with another identifier removes a whole class of defect at the type level.

## Change by addition

Add optional fields and new operations freely. Removing a field, narrowing an accepted value, tightening
validation, or changing a default is a breaking change even when the type checker stays quiet — a caller
relying on the old behaviour breaks at runtime, in production, not at build time.

When something genuinely must go: ship the replacement, migrate callers, then remove — in three steps, not
one. Keep one version live at a time where you can; parallel versions multiply the surface Hyrum's Law
applies to.

## Naming is part of the contract

Same concept, same word, everywhere. A field called `user_id` in one operation and `userId` in the next is a
defect the compiler cannot see and every caller pays for. Match the surrounding interface's conventions even
where you would have chosen differently — consistency is worth more here than your preference.
