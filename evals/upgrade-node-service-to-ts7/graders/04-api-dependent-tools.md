---
type: llm
focus: trace
weight: 1
---

The response flags that TypeScript 7.0 ships without a compiler API, so tools that load TypeScript as a library — here ts-node and ts-jest — won't work with 7.0 as-is, and gives a concrete path: keep them on TypeScript 6.0 via the official `@typescript/typescript6` compatibility package / npm aliasing, or replace them (e.g. tsx, swc/@swc/jest, Node's type stripping).
