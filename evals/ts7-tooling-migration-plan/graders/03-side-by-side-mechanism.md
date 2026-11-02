---
type: llm
focus: trace
weight: 1
---

The response gives the official side-by-side mechanism: the `@typescript/typescript6` package (which provides `tsc6` and re-exports the 6.0 API), e.g. aliasing `typescript` to `npm:@typescript/typescript6` for library consumers while installing 7.0 under another name (such as `"@typescript/native": "npm:typescript@^7.0.2"`) to get the 7.0 `tsc`. A plan that only says "pin TypeScript 6" without explaining how both versions coexist fails.
