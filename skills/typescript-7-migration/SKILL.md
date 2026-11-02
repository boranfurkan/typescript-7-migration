---
name: typescript-7-migration
description: Upgrades projects to TypeScript 7 (the native Go compiler, released July 2026) using the official 6.0 and 7.0 release notes. Use whenever a task involves TypeScript 7, TS7, tsgo, @typescript/native-preview, the native TypeScript compiler, upgrading TypeScript from 5.x or 6.x, tsconfig errors after a TypeScript upgrade (target es5, moduleResolution node, baseUrl, esModuleInterop, downlevelIteration, outFile, ignoreDeprecations), build output suddenly landing in dist/src, @types no longer found after upgrading, or tools that break on TypeScript 7 — typescript-eslint, ts-node, ts-jest, vue-tsc/Volar, Angular templates, ts-patch, custom transformers, or scripts using the compiler API.
---

# TypeScript 7 migration

TypeScript 7.0 (GA 2026-07-08) is the Go-native port of the compiler: about 10× faster checking, installed
from the normal `typescript` package, with the binary still called `tsc`. Most breaking changes were announced
as deprecations in 6.0 and are hard errors in 7.0. The two things people trip over are:

1. **7.0 ships without a compiler API.** Anything that loads `typescript` as a library stays on 6.0 until the new
   API arrives in 7.1, and that API will be different.
2. **Two defaults changed silently:** `types` is now `[]` and `rootDir` is the tsconfig's directory.

These facts are from the official announcements as of 7.0. If you can check newer release notes or
`npm view typescript version`, do; 7.1+ may change the API story.

## Workflow

```
- [ ] 1. Inventory every tsconfig (follow "extends") and everything that imports `typescript`
- [ ] 2. Split tooling: moves to 7.0 now vs. stays on 6.0
- [ ] 3. Fix tsconfig: hard errors + changed defaults
- [ ] 4. Fix code the new rules reject
- [ ] 5. Set up 6.0 and 7.0 side by side if anything stays on 6.0
- [ ] 6. Verify and report what moved, what didn't, and what you couldn't check
```

### 1. Inventory

- All tsconfig files, including `extends` targets (`@tsconfig/*`, `@vue/tsconfig`, framework presets). A removed
  option inherited from a preset is still an error.
- Dependencies and scripts that use the TypeScript **API**: typescript-eslint (type-aware rules), ts-node,
  ts-jest, vue-tsc / Volar, Svelte, Astro, MDX and Angular template checkers, ts-patch and transformer plugins
  (`compilerOptions.plugins` with `transform`), fork-ts-checker, api-extractor, typedoc, `require("typescript")`
  or `import ts from "typescript"` in your own scripts, and language-service plugins.

### 2. What can move to 7.0 now

| Moves to 7.0 | Stays on 6.0 (no API in 7.0) |
|---|---|
| `tsc`, `tsc --noEmit`, `tsc -b` type-checking and emit | typescript-eslint (doesn't support 7.0; peer range `<6.1`) |
| Editors via the TS 7 language server (VS Code: `TypeScriptTeam.native-preview` extension) | vue-tsc / Volar, Svelte, Astro, MDX checkers |
| Bundlers that strip types themselves (esbuild, Vite, swc, Bun) | Angular template type-checking in editors (Angular CLI checking can use 7.0) |
| | ts-node, ts-jest, ts-patch, custom transformers, compiler-API scripts, language-service plugins |

For runners that only need type stripping, consider replacing ts-node/ts-jest with tsx, @swc/jest or Node's
built-in type stripping instead of keeping 6.0 for them.

### 3. tsconfig: hard errors in 7.0

| Option | Replace with |
|---|---|
| `"target": "es5"` | `es2015` or later (e.g. `es2022`); use another compiler if you must ship ES5 |
| `"downlevelIteration"` | remove it |
| `"moduleResolution": "node"` / `"node10"` / `"classic"` | `"nodenext"` (with `"module": "nodenext"`) for Node; `"bundler"` for bundlers/Bun |
| `"module": "amd"` / `"umd"` / `"systemjs"` / `"none"` | an ES module target + a bundler |
| `"baseUrl"` | remove; write `paths` relative to the tsconfig: `"@/*": ["./src/*"]`. If baseUrl was a lookup root, add `"*": ["./src/*"]` |
| `"esModuleInterop": false`, `"allowSyntheticDefaultImports": false` | remove; change `import * as x from "cjs-pkg"` to `import x from "cjs-pkg"` where the namespace was called or constructed |
| `"alwaysStrict": false` | remove; rename identifiers that are reserved words in strict mode |
| `"outFile"` | remove; bundle with esbuild, Rollup, Vite, etc. |
| `"ignoreDeprecations": "6.0"` | only bridged 6.0; fix the underlying options |
| `tsc file.ts` while a tsconfig.json exists | error TS5112; add `--ignoreConfig` |

### 3b. Defaults that changed (6.0, kept in 7.0)

| Option | New default | What breaks / fix |
|---|---|---|
| `types` | `[]` | `describe`, `process` etc. not found → list them: `"types": ["node", "jest"]` (`["*"]` restores old behaviour) |
| `rootDir` | directory of the tsconfig | output moves to `dist/src/…` → set `"rootDir": "./src"` (keep tests in a separate tsconfig) |
| `strict` | `true` | new errors in loose projects → fix, or set `"strict": false` explicitly |
| `module` | `esnext` | set `module` explicitly for CommonJS/Node projects |
| `target` | latest ES (the version just before `esnext`) | set explicitly if you ship to older runtimes |
| `noUncheckedSideEffectImports` | `true` | side-effect imports of missing modules now error |
| `libReplacement` | `false` | — |
| `stableTypeOrdering` | `true`, can't be disabled in 7.0 | rare inference changes → add explicit type arguments |

`dom.iterable` and `dom.asynciterable` are part of `dom` since 6.0.

### 4. Code the new rules reject

- `import * as express from "express"` used as a function/constructor → `import express from "express"`.
- `module Foo { }` namespace declarations → `namespace Foo { }` (`declare module "pkg"` is fine).
- Import assertions `assert { type: "json" }` → import attributes `with { type: "json" }`.
- Generic calls with function-expression arguments are checked more strictly (6.0) → add explicit type arguments.
- JS/JSDoc projects (`checkJs`): use `typeof` for values used as types, `class` instead of `@class`, `any`
  instead of a bare `?`; closure-style function types are no longer supported.
- Template-literal type utilities that split strings now see whole Unicode code points, not UTF-16 halves.

### 5. Run 6.0 and 7.0 side by side

The official compatibility package `@typescript/typescript6` provides `tsc6` and re-exports the 6.0 API. Point
library consumers at it under the name `typescript`, and install 7.0 under another name to get its `tsc`:

```jsonc
{
  "devDependencies": {
    "typescript": "npm:@typescript/typescript6",    // what typescript-eslint, vue-tsc, ts-jest import (6.0 API, bin: tsc6)
    "@typescript/native": "npm:typescript@^7.0.2"   // the 7.0 compiler (bin: tsc)
  },
  "scripts": {
    "typecheck": "tsc --noEmit",                    // 7.0
    "typecheck:vue": "vue-tsc --noEmit"             // still 6.0 via the alias
  }
}
```

Say which commands run on which version, and re-check when TypeScript 7.1 (with a new API) ships.

### 6. Verify and report

- Safest path: upgrade to **6.0 first**, enable `"stableTypeOrdering": true`, remove `ignoreDeprecations`, and fix
  everything. Code that compiles cleanly there should compile the same on 7.0. (The flag can slow 6.0 by about 25%;
  it's a diagnostic step.)
- Run `tsc --noEmit` on 7.0. If anything stays on 6.0, also run `tsc6 --noEmit` and compare.
- On small CI runners, `--checkers <n>` (default 4) caps the parallel type-checkers; `--builders <n>` caps parallel
  project builds under `-b`; `--singleThreaded` disables parallelism.
- State the reason in plain words whenever any tool stays on 6.0: "TypeScript 7.0 ships without a compiler API;
  a new, different API is planned for 7.1 (in beta as of 2026-11), so tools that import `typescript` as a library
  (typescript-eslint, vue-tsc, ts-jest, ts-node, ts-patch transformers, `ts.createProgram` scripts) can't run on 7.0."
  Name each affected tool in the repo and say it either stays on 6.0 via the alias or is replaced.
- Report: the tsconfig changes, the code changes, which tools stay on 6.0 and why, and anything you couldn't
  verify (for example, no network for `npm install`).

Sources: "Announcing TypeScript 7.0" and "Announcing TypeScript 6.0" (Microsoft DevBlogs).
