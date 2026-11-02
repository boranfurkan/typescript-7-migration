---
tags: [ts7, debugging]
max_turns: 50
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

We bumped TypeScript from 5.7 to 7.0 and nothing else. Now tsc says it can't find `describe`, `it` and `process` even though @types/jest and @types/node are installed, and the build output moved — dist/ now contains a src/ folder (dist/src/server.js), so `node dist/server.js` fails. What changed and what's the right fix? The output of our CI run is in ci.log.

Input files: ci.log, package.json, src/math.ts, src/server.ts, test/math.test.ts, tsconfig.json, tsconfig.test.json
