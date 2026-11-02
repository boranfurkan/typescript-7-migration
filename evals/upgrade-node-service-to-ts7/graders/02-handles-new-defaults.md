---
type: llm
focus: trace
weight: 1
---

The response accounts for TypeScript 6/7's changed defaults: it sets "rootDir" explicitly (e.g. "./src", because rootDir now defaults to the tsconfig's directory and output would otherwise move to dist/src) AND lists the needed global types explicitly (e.g. "types": ["node", "jest"], because types now defaults to []).
