# TypeScript 7 Migration Skill

**Lets your coding agent upgrade projects to TypeScript 7 correctly, using facts from the official release notes
instead of guesses.**
An [Agent Skills](https://agentskills.io) skill (`SKILL.md`). Tested in Claude Code; `npx skills` installs it for other agents that read Agent Skills, which we haven't tested.

TypeScript 7.0 (July 2026) is the Go-native compiler: about 10× faster type-checking. It shipped after the training
cutoff of today's models. They know the general direction (6.0 deprecations, "native port") but hedge or guess on
the details that decide whether your upgrade works:

- **7.0 has no compiler API.** typescript-eslint, vue-tsc/Volar, ts-node, ts-jest, ts-patch transformers and any
  script using `ts.createProgram` must stay on 6.0, via the official `@typescript/typescript6` package.
- **Hard errors:** `target: es5`, `downlevelIteration`, `moduleResolution: node`, `baseUrl`,
  `esModuleInterop: false`, `outFile`, AMD/UMD/System modules, and more.
- **Silent default changes:** `types` is now `[]` ("Cannot find name 'describe'") and `rootDir` is the tsconfig's
  directory (output moves to `dist/src/`).
- **How to run 6.0 and 7.0 side by side** with npm aliases.

## Install

**Claude Code (plugin):**
```
/plugin marketplace add boranfurkan/typescript-7-migration
/plugin install typescript-7-migration@typescript-7-migration
```

**Any agent supporting Agent Skills:**
```bash
npx skills add boranfurkan/typescript-7-migration
```

**Manual:** copy `skills/typescript-7-migration/` into your agent's skills folder (Claude Code: `~/.claude/skills/`).

Then ask your agent something like *"upgrade this repo to TypeScript 7"* or *"why can't tsc find describe after
upgrading?"*. In our evals it activated by itself in 11 of 12 runs.

## Example

> **You:** We bumped TypeScript from 5.7 to 7.0. Now tsc can't find `describe` or `process` even though
> @types/jest and @types/node are installed, and the build moved to `dist/src/server.js`.

With the skill, the agent names both silent default changes (`types` is now `[]`, `rootDir` is now the tsconfig's
directory) and fixes them:

```jsonc
// tsconfig.json
"rootDir": "./src",
"types": ["node", "jest"]
```

## Eval results

In offline evals the skill raised graders passed from 10/18 to 17/18 on Sonnet 5.5 and from 7/18 to 15/18 on Haiku 5.5.
Small samples; read the caveats below.


Graders passed (LLM judge = Sonnet, 3 votes per grader), 2 runs per arm, one table cell per run.

| Case | Sonnet without | Sonnet with | Haiku without | Haiku with |
|---|---|---|---|---|
| ts7-tooling-migration-plan (3 graders) | 0/3, 0/3 | 3/3, 3/3 | 0/3, 0/3 | 2/3, 2/3 |
| upgrade-node-service-to-ts7 (4 graders) | 3/4, 4/4 | 4/4, 4/4 | 2/4, 2/4 | 3/4, 4/4 |
| ts7-post-upgrade-breakage (2 graders) | 1/2, 2/2 | 2/2, 1/2 | 2/2, 1/2 | 2/2, 2/2 |
| **Total** | **10/18** | **17/18** | **7/18** | **15/18** |

## Read this before trusting the numbers
- **Small samples:** 2 runs per arm per case. Differences of a point or two are noise.
- **Offline agents:** the agents had no web tools. Real agents with web access may find these facts themselves, so real-world gains are likely smaller.
- **Same author:** the skill and the graders were written by the same person from the same release notes.
- **One mechanism-specific grader:** it requires the `@typescript/typescript6` side-by-side mechanism specifically.
- **Strict graders:** the two with-skill misses are judged strictness, not wrong answers. Haiku tooling grader 1 bundles "no API in 7.0", "new API in 7.1" and "ts-patch can't run" into one check; both answers got the substance right but omitted the 7.1 mention. Sonnet post-upgrade run 2 explained the `types` default and fixed it, but split `node`/`jest` across two tsconfigs, and the judge voted 1-2.
- **Skill edited mid-evaluation:** after the first Haiku with-skill runs I added a line to SKILL.md telling the agent to state the "7.0 has no compiler API" reason explicitly, then re-ran Haiku on the tooling and upgrade cases. Scores did not improve (tooling 2/3, 2/3 again; upgrade 4/4, 3/4), so the table keeps the original runs. The Sonnet runs used the earlier SKILL.md wording.
- **Facts date:** as of TypeScript 7.0, re-checked 2026-11-02 (7.1 was still in beta).

The same author also made a [benchmark of a data-analysis skill](https://github.com/boranfurkan/trustworthy-data-analysis) where gains were much smaller.

## What the agent does with it

1. **Inventory:** every tsconfig (including `extends` presets) and everything that imports `typescript` as a library.
2. **Split tooling:** what can move to 7.0 now (`tsc`, `tsc -b`, editors, type-stripping bundlers) and what must stay
   on 6.0 until the 7.1 API (typescript-eslint, vue-tsc, ts-jest, ts-node, transformers, compiler-API scripts).
3. **Fix tsconfig:** a replacement table for every option that's now a hard error, plus the changed defaults.
4. **Fix code:** namespace imports of CommonJS packages, `module` namespaces, import assertions, JSDoc changes.
5. **Side-by-side setup:**
   ```jsonc
   "typescript": "npm:@typescript/typescript6",   // 6.0 API for typescript-eslint, vue-tsc, ts-jest (bin: tsc6)
   "@typescript/native": "npm:typescript@^7.0.2"  // the 7.0 compiler (bin: tsc)
   ```
6. **Verify and report:** go through 6.0 with `stableTypeOrdering` first, use the `--checkers` flag on small CI
   runners, and list what moved, what didn't, and what couldn't be checked.

## Evals

Built evals-first. Each case in [`evals/`](evals/) is a small realistic project with an upgrade request:

| Case | What it checks |
|---|---|
| `upgrade-node-service-to-ts7` | Upgrade an Express service from a TS 5 config (`es5`, `moduleResolution: node`, `baseUrl`, `esModuleInterop: false`, ts-node/ts-jest) |
| `ts7-tooling-migration-plan` | Plan for Vue + vue-tsc, type-aware typescript-eslint, ts-patch, and a compiler-API docs script |
| `ts7-post-upgrade-breakage` | Diagnose "cannot find describe/process" and output moving to `dist/src` after the upgrade |

Graders state facts from the official announcements, so the judge checks answers against the release notes rather
than its own memory. The agent runs offline, with no web tools. Reproduce with Claude Code ≥ 2.1.269:

```bash
claude plugin eval . --scaffold --allow-tools Write,Edit,Bash --model haiku
```

## Sources

- [Announcing TypeScript 7.0](https://devblogs.microsoft.com/typescript/announcing-typescript-7-0/) (Microsoft DevBlogs, 2026-07-08)
- [Announcing TypeScript 6.0](https://devblogs.microsoft.com/typescript/announcing-typescript-6-0/) (Microsoft DevBlogs)
- Notes and the baseline knowledge probe: [`research/01-official-facts.md`](research/01-official-facts.md)

Facts are as of TypeScript 7.0 (re-checked 2026-11-02). TypeScript 7.1 Beta (2026-10-20) previews a new, different compiler API; stable 7.1 is planned for 2026-11-24, and typescript-eslint still does not support TS 7. This skill will be updated when 7.1 is stable.

## License

MIT
