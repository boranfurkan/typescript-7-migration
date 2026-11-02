# TypeScript 7.0 — facts from official sources (collected 2026-11-02)

Sources:
- "Announcing TypeScript 7.0" (Microsoft DevBlogs, 2026-07-08): https://devblogs.microsoft.com/typescript/announcing-typescript-7-0/
- "Announcing TypeScript 6.0" (Microsoft DevBlogs): https://devblogs.microsoft.com/typescript/announcing-typescript-6-0/
- typescript-eslint status (secondary, mid-2026): issue #12518 closed "not planned"; peer range >=4.8.4 <6.1.0; throws "typescript-eslint does not support TS 7.0" at load.

## Install / binaries (7.0 announcement)
- `npm install -D typescript` → `tsc` (Go-native compiler). Nightlies return under `typescript@next`.
- Previews used `@typescript/native-preview` (binary `tsgo`). Stable = plain `typescript` + `tsc`.
- Keep 6.0 side by side: `@typescript/typescript6` → `tsc6` executable + re-exports the 6.0 API.
- Tools that import `typescript` as a library (typescript-eslint, …): alias `typescript@npm:@typescript/typescript6`
  (gives only `tsc6`), and add `@typescript/native` as `npm:typescript@^7.0.2` to get the 7.0 `tsc`.

## Not supported in 7.0
- No compiler API ("it does not ship with an API"); a new, different API is expected in 7.1.
- Embedded-language tooling depending on the API (Volar: Vue, MDX, Astro, Svelte, Angular templates) likely won't work → keep 6.0 for those editors; Angular teams can use 7.0 for CLI checking.
- Language server plugins not supported → use 7.0 only "where language server plugins are not required".
- (Implied) ts-patch / custom transformers that patch the JS compiler cannot work with the native binary.

## Defaults (6.0 introduced, 7.0 keeps)
strict=true · module=esnext · target=latest ES (es2025 in 6.0; "the version just before esnext" in 7.0) ·
noUncheckedSideEffectImports=true · libReplacement=false · stableTypeOrdering=true (7.0, can't disable) ·
rootDir=directory containing tsconfig.json (was inferred) · types=[] (was all @types; restore with ["*"]).

## Hard errors in 7.0 (deprecated in 6.0; `"ignoreDeprecations": "6.0"` only bridges 6.0)
- target es5 → ES2015+ or external compiler for ES5 output
- downlevelIteration → remove
- moduleResolution node/node10/classic → nodenext (Node) or bundler (bundlers/Bun)
- module amd/umd/systemjs/none → ESM target or a bundler
- baseUrl → remove; prefix paths ("./src/app/*"); catch-all "*": ["./src/*"] if used as lookup root
- esModuleInterop:false / allowSyntheticDefaultImports:false → can't be false; use default imports
- alwaysStrict:false → everything strict; rename reserved-word identifiers
- outFile → removed; use a bundler
- `module` keyword for namespaces → `namespace` (`declare module "x"` still fine)
- import `asserts` → `with`
- `/// <reference no-default-lib="true"/>` → --noLib / --libReplacement
- CLI file paths while a tsconfig.json exists → error TS5112; use --ignoreConfig

## Migration steps (official)
1. Move to 6.0 first; code that compiles cleanly there with stableTypeOrdering on and no ignoreDeprecations should
   compile the same in 7.0. `--stableTypeOrdering` in 6.0: matches 7.0 ordering, can slow checking ~25%, can expose
   inference errors (fix with explicit type args/annotations); diagnostic, not permanent.
2. tsconfig outside src → add "rootDir": "./src".
3. Global types → list them: "types": ["node", "jest"].
4. Remove deprecated options. Experimental `ts5to6` tool automates baseUrl/rootDir changes.
- 6.0: dom.iterable / dom.asynciterable folded into dom.
- 6.0: function expressions in generic calls checked more strictly → explicit type args sometimes needed.

## Behaviour changes in 7.0
- Template literal inference keeps Unicode code points intact (HeadTail<"😀abc"> → ["😀","abc"]).
- JS (JSDoc) checking follows TS rules more closely: `typeof` for values used as types, `class` not `@class`,
  `any` not standalone `?`, closure-style function types unsupported (see CHANGES.md).

## Performance flags
--checkers N (type-checker workers, default 4; lower on small CI runners) · --builders N (parallel project builds
under --build) · --singleThreaded.

## Editor
VS Code: extension `TypeScriptTeam.native-preview`; commands "Enable/Disable TypeScript 7 Language Server";
built-in support "in the coming weeks". Visual Studio: automatic. Others: LSP.

## Timeline
7.1 expected to bring the new API; feature releases every 3–4 months.

## Baseline model knowledge (probe 2026-11-02, Haiku 5.5 / Sonnet 5.5, no tools)
Both know: native Go port; 6.0 deprecation list (mostly); default changes strict/module/types/rootDir; no JS API.
Both hedge/unsure: binary name (tsc vs tsgo), @typescript/typescript6 (Sonnet "vaguely recalls"), alias trick,
typescript-eslint status, --checkers/--builders, VS Code extension, stableTypeOrdering, Unicode/JSDoc changes.

## Re-check 2026-11-02
- 7.1 Beta announced 2026-10-20 (devblogs.microsoft.com/typescript/announcing-typescript-7-1-beta/): new modular API (typescript/sync, /async, /fs), snapshots, disposable objects; watch/incremental/build APIs not in 7.1. Iteration plan (#63703): RC 2026-11-10, stable 2026-11-24 (planned).
- typescript-eslint: still no TS 7 support (#12518); draft PR #12803 experimental 7.1 support. SKILL.md "stays on 6.0 until 7.1 API" remains correct today; revisit after 7.1 stable.
