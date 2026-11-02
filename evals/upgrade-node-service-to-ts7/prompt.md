---
tags: [ts7, upgrade]
max_turns: 50
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Upgrade this service to TypeScript 7 (the stable 7.0 release). Update package.json, tsconfig.json and any source files that need to change, and tell me anything that will break or that you couldn't verify. You're offline, so you can't npm install.

Input files: jest.config.js, package.json, src/index.ts, src/orders.ts, test/orders.test.ts, tsconfig.json
