---
tags: [ts7, tooling]
max_turns: 50
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

We want to move this repo to TypeScript 7 this sprint because of the 10x faster type-checking. Look at our setup (Vue + vue-tsc, type-aware typescript-eslint, ts-patch with a path transformer, and a docs script built on the compiler API) and give me a concrete migration plan: what can move to 7.0 now, what can't, and exactly how to run both versions side by side if needed.

Input files: eslint.config.js, package.json, scripts/gen-api-docs.mjs, src/api/index.ts, tsconfig.json
