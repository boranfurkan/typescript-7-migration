---
type: llm
focus: trace
weight: 1
---

The updated tsconfig.json no longer contains any option that is a hard error in TypeScript 7.0: target "es5" is raised (e.g. es2022 or later), downlevelIteration is removed, moduleResolution "node" is replaced (nodenext with a matching module, or bundler), baseUrl is removed with paths rewritten relative to the config (e.g. "@/*": ["./src/*"]), and esModuleInterop: false is removed or set to true.
