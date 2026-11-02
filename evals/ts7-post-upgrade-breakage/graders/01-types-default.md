---
type: llm
focus: trace
weight: 1
---

The response explains that since TypeScript 6.0 (and in 7.0) the `types` compiler option defaults to an empty list, so installed @types packages (node, jest) are no longer included automatically, and fixes it by listing them, e.g. "types": ["node", "jest"].
