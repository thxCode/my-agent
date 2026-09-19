---
name: frontend-ui-engineering
description: Build UI that reuses the project's own design system, states every async outcome, and is keyboard-reachable.
---

# Frontend UI engineering

Distilled from [`frontend-ui-engineering`](https://github.com/addyosmani/agent-skills/tree/main/skills/frontend-ui-engineering)
(MIT, Copyright (c) 2025 Addy Osmani); see `CREDITS.md`.

Read when a `my-build` task renders something a person looks at. Everything here yields to the project's own
system — this is the floor for a project that documents nothing, not a house style to impose on one that does.

## The project's own system outranks every rule below

Before writing a component, find what the project already standardizes and use it. Many projects ship their
own review skill under `.claude/skills/` naming their primitives, their status-colour map, their drawer and
confirm-dialog components; where one exists, it is the specification and this file is background.

**The most common defect in generated UI is a hand-rolled version of something the project already has.**
A bespoke drawer beside the project's drawer primitive, a raw colour literal beside its semantic token, a
custom confirm beside its delete dialog. Look before you build; grep the component directory for the concept,
not for the word you happened to choose.

Drive spacing, colour, and typography from the theme's named tokens. A hardcoded value the theme already
names will be wrong the first time the theme changes, and nobody will find it.

## Colour carries meaning, so pick it by meaning

A status colour is chosen from what the value *means*, never from what looks right in this screen. Two
different meanings must not share a colour, and one meaning must not change colour between screens. Map
domain states through the project's status map rather than branching on the raw string at the call site.

## Every async outcome is a visible state

Four states, all of them designed: loading, empty, error, and loaded. A screen that renders nothing while
fetching, or renders an empty table identically whether the list is empty or the request failed, is broken
regardless of how the happy path looks.

An action that can be fired twice must be locked while in flight. A failed row must surface its message, not
just turn a colour — a red dot the user cannot interrogate is a dead end.

## Accessibility is where generated UI fails hardest

Look here first in review, because these are cheap to fix and invisible until someone is blocked:

- An interactive element must be a real `button` or `a`. An `onClick` on a `div` is unreachable by keyboard
  and invisible to a screen reader.
- An icon-only control needs an accessible name. The icon is not the label.
- A form field needs a real associated label; a placeholder disappears the moment typing starts.
- A dialog or drawer closes on `Escape` and keeps focus inside while open, returning it on close.
- Contrast and focus rings are requirements, not polish. Never remove a focus outline without replacing it
  with a visible one.

## Resist the generated look

The tell is uniformity: everything the same weight, evenly spaced, nothing leading the eye. Establish
hierarchy by size and weight before reaching for colour, keep the type scale small and the spacing scale
consistent, and let density match the surface — a data-dense admin table and a marketing page have opposite
right answers, and applying one to the other is the mistake.

## Verify in a browser, not by reading

A component that compiles is not a component that works. Use `browser-testing` for interactive
verification (clicks, console, network) and `crawl4ai-search` for a rendered screenshot. Responsive claims in
particular hold only once checked at the widths the project actually supports.
