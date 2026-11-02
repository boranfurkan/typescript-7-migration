# Eval results: typescript-7-migration

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
- **Facts date:** as of TypeScript 7.0, re-checked 2026-11-02 (7.1 was still in beta).
