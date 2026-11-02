---
type: llm
focus: trace
weight: 1
---

The response explains that `rootDir` now defaults to the directory containing tsconfig.json (instead of being inferred as the common directory of the input files, which was src/), which is why output moved to dist/src, and fixes it with an explicit "rootDir": "./src" in tsconfig.json.
