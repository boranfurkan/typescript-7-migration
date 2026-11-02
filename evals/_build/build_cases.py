#!/usr/bin/env python3
"""Build the eval suite for typescript-7-migration.

Each case is a small, realistic project plus an upgrade request. Graders state facts from the official
"Announcing TypeScript 7.0" (2026-07-08) and "Announcing TypeScript 6.0" posts, so the LLM judge checks
the response against them rather than against its own memory.

Usage: python3 evals/_build/build_cases.py
"""
import json
import shutil
from pathlib import Path

EVALS = Path(__file__).resolve().parents[1]

SETTINGS = """---
tags: [{tags}]
max_turns: 50
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---
"""
PLACE_FILES = """#!/usr/bin/env bash
set -eu
cp -R "$(dirname "$0")/files/." .
"""
GRADER = """---
type: llm
focus: trace
weight: 1
---

{text}
"""


def case(name, tags, prompt, files, expected, graders):
    d = EVALS / name
    if d.exists():
        shutil.rmtree(d)
    (d / "files").mkdir(parents=True)
    (d / "graders").mkdir()
    for rel, content in files.items():
        p = d / "files" / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content if isinstance(content, str) else json.dumps(content, indent=2) + "\n")
    listing = ", ".join(sorted(files))
    (d / "prompt.md").write_text(SETTINGS.format(tags=", ".join(tags)) + "\n" + prompt.strip() + f"\n\nInput files: {listing}\n")
    (d / "case.yaml").write_text('schema_version: "1.1"\n' f"name: {name}\n" "expected_outcome: |\n"
                                 + "".join("  " + l + "\n" for l in expected.strip().splitlines())
                                 + "context:\n  scaffold_script: place-files.sh\n")
    ps = d / "place-files.sh"
    ps.write_text(PLACE_FILES)
    ps.chmod(0o755)
    for i, (slug, text) in enumerate(graders, 1):
        (d / "graders" / f"{i:02d}-{slug}.md").write_text(GRADER.format(text=text.strip()))


# ----------------------------------------------------------------------------- case 1: upgrade a Node service

SERVICE_PKG = {
    "name": "orders-service", "version": "1.4.0", "private": True,
    "scripts": {"build": "tsc -p tsconfig.json", "dev": "ts-node src/index.ts", "test": "jest", "typecheck": "tsc --noEmit"},
    "dependencies": {"express": "^4.21.2"},
    "devDependencies": {"typescript": "~5.8.3", "ts-node": "^10.9.2", "jest": "^29.7.0", "ts-jest": "^29.2.5",
                        "@types/express": "^4.17.21", "@types/jest": "^29.5.14", "@types/node": "^22.10.2"},
}
SERVICE_TSCONFIG = """{
  "compilerOptions": {
    "target": "es5",
    "lib": ["es2017"],
    "downlevelIteration": true,
    "module": "commonjs",
    "moduleResolution": "node",
    "baseUrl": ".",
    "paths": { "@/*": ["src/*"] },
    "esModuleInterop": false,
    "outDir": "dist",
    "sourceMap": true,
    "strict": false,
    "noImplicitAny": true
  },
  "include": ["src/**/*.ts"]
}
"""
SERVICE_INDEX = """import * as express from "express";
import { listOrders, Order } from "@/orders";

const app = express();

app.get("/orders", (_req, res) => {
  const totals: Array<[string, number]> = [];
  for (const [id, order] of listOrders()) {
    totals.push([id, order.items.reduce((s, i) => s + i.qty * i.price, 0)]);
  }
  res.json(totals);
});

app.listen(Number(process.env.PORT ?? 3000));
export type { Order };
"""
SERVICE_ORDERS = """export interface Order {
  id: string;
  items: { sku: string; qty: number; price: number }[];
}

const store = new Map<string, Order>([
  ["o-1", { id: "o-1", items: [{ sku: "A", qty: 2, price: 9.5 }] }],
]);

export function listOrders(): Map<string, Order> {
  return store;
}
"""
SERVICE_TEST = """import { listOrders } from "../src/orders";

describe("listOrders", () => {
  it("returns the seeded order", () => {
    expect(listOrders().get("o-1")?.items.length).toBe(1);
  });
});
"""
SERVICE_JEST = """module.exports = {
  preset: "ts-jest",
  testEnvironment: "node",
  moduleNameMapper: { "^@/(.*)$": "<rootDir>/src/$1" },
};
"""


def c_upgrade_service():
    case(
        "upgrade-node-service-to-ts7",
        ["ts7", "upgrade"],
        """Upgrade this service to TypeScript 7 (the stable 7.0 release). Update package.json, tsconfig.json and any source files that need to change, and tell me anything that will break or that you couldn't verify. You're offline, so you can't npm install.""",
        {"package.json": SERVICE_PKG, "tsconfig.json": SERVICE_TSCONFIG, "src/index.ts": SERVICE_INDEX,
         "src/orders.ts": SERVICE_ORDERS, "test/orders.test.ts": SERVICE_TEST, "jest.config.js": SERVICE_JEST},
        """Per the official 6.0/7.0 announcements: target es5, downlevelIteration, moduleResolution node, baseUrl and
esModuleInterop:false are hard errors in 7.0 → raise target, drop downlevelIteration, use nodenext (or bundler),
remove baseUrl and write paths as "./src/*", drop esModuleInterop:false and switch `import * as express` to a default
import. New defaults: rootDir = tsconfig directory (set "rootDir": "./src" or output moves to dist/src) and types = []
(list "node", "jest"). 7.0 ships no compiler API, so ts-node and ts-jest (which load the TypeScript API) won't work on
7.0 → keep them on 6.0 via @typescript/typescript6 / npm aliasing, or switch runners.""",
        [
            ("removes-hard-errors", """The updated tsconfig.json no longer contains any option that is a hard error in TypeScript 7.0: target "es5" is raised (e.g. es2022 or later), downlevelIteration is removed, moduleResolution "node" is replaced (nodenext with a matching module, or bundler), baseUrl is removed with paths rewritten relative to the config (e.g. "@/*": ["./src/*"]), and esModuleInterop: false is removed or set to true."""),
            ("handles-new-defaults", """The response accounts for TypeScript 6/7's changed defaults: it sets "rootDir" explicitly (e.g. "./src", because rootDir now defaults to the tsconfig's directory and output would otherwise move to dist/src) AND lists the needed global types explicitly (e.g. "types": ["node", "jest"], because types now defaults to [])."""),
            ("fixes-namespace-import", """The response updates src/index.ts from `import * as express from "express"` to a default import (`import express from "express"`) or otherwise explains that this import must change because esModuleInterop can no longer be false."""),
            ("api-dependent-tools", """The response flags that TypeScript 7.0 ships without a compiler API, so tools that load TypeScript as a library — here ts-node and ts-jest — won't work with 7.0 as-is, and gives a concrete path: keep them on TypeScript 6.0 via the official `@typescript/typescript6` compatibility package / npm aliasing, or replace them (e.g. tsx, swc/@swc/jest, Node's type stripping)."""),
        ],
    )


# ----------------------------------------------------------------------------- case 2: tooling plan

TOOLING_PKG = {
    "name": "storefront", "private": True,
    "scripts": {"typecheck": "vue-tsc --noEmit", "build": "vite build", "lint": "eslint .",
                "prepare": "ts-patch install -s", "docs": "node scripts/gen-api-docs.mjs"},
    "devDependencies": {"typescript": "~5.9.2", "vue-tsc": "^2.2.0", "@vue/tsconfig": "^0.7.0", "vite": "^6.0.0",
                        "eslint": "^9.17.0", "typescript-eslint": "^8.18.0", "ts-patch": "^3.3.0",
                        "typescript-transform-paths": "^3.5.2"},
}
TOOLING_ESLINT = """import tseslint from "typescript-eslint";

export default tseslint.config(
  ...tseslint.configs.recommendedTypeChecked,
  { languageOptions: { parserOptions: { projectService: true, tsconfigRootDir: import.meta.dirname } } },
);
"""
TOOLING_TSCONFIG = """{
  "extends": "@vue/tsconfig/tsconfig.dom.json",
  "compilerOptions": {
    "strict": true,
    "moduleResolution": "bundler",
    "paths": { "@/*": ["./src/*"] },
    "plugins": [{ "transform": "typescript-transform-paths" }]
  },
  "include": ["src/**/*.ts", "src/**/*.vue"]
}
"""
TOOLING_DOCS = """import ts from "typescript";

const program = ts.createProgram(["src/api/index.ts"], { strict: true });
const checker = program.getTypeChecker();
for (const sf of program.getSourceFiles()) {
  if (sf.isDeclarationFile) continue;
  ts.forEachChild(sf, (node) => {
    if (ts.isFunctionDeclaration(node) && node.name) {
      const sig = checker.getSignatureFromDeclaration(node);
      console.log(`${node.name.text}${sig ? checker.signatureToString(sig) : ""}`);
    }
  });
}
"""


def c_tooling_plan():
    case(
        "ts7-tooling-migration-plan",
        ["ts7", "tooling"],
        """We want to move this repo to TypeScript 7 this sprint because of the 10x faster type-checking. Look at our setup (Vue + vue-tsc, type-aware typescript-eslint, ts-patch with a path transformer, and a docs script built on the compiler API) and give me a concrete migration plan: what can move to 7.0 now, what can't, and exactly how to run both versions side by side if needed.""",
        {"package.json": TOOLING_PKG, "eslint.config.js": TOOLING_ESLINT, "tsconfig.json": TOOLING_TSCONFIG,
         "scripts/gen-api-docs.mjs": TOOLING_DOCS, "src/api/index.ts": "export function getCart(id: string): Promise<unknown> {\n  return fetch(`/api/cart/${id}`).then((r) => r.json());\n}\n"},
        """7.0 has no compiler API (a new, different API is planned for 7.1). Everything here that loads TypeScript as a
library stays on 6.0: typescript-eslint (doesn't support TS 7; peer range <6.1), vue-tsc/Volar (Vue template checking,
needs the API), ts-patch transformers, and the ts.createProgram docs script. The official path is the
@typescript/typescript6 package (tsc6 + the 6.0 API), e.g. alias "typescript": "npm:@typescript/typescript6" for the
tools and add the 7.0 compiler under another name ("@typescript/native": "npm:typescript@^7.0.2") for plain tsc
checking. Move to 6.0 first and clear deprecations (with stableTypeOrdering) before relying on 7.0.""",
        [
            ("no-api-in-7", """The response states that TypeScript 7.0 ships without a compiler API (a new, different API is expected in 7.1), and concludes that the docs script using ts.createProgram and the ts-patch transformer (typescript-transform-paths) cannot run on 7.0."""),
            ("eslint-and-vue", """The response says that type-aware typescript-eslint and vue-tsc (Volar-based Vue template checking) cannot use TypeScript 7.0 yet and must keep running on TypeScript 6.0."""),
            ("side-by-side-mechanism", """The response gives the official side-by-side mechanism: the `@typescript/typescript6` package (which provides `tsc6` and re-exports the 6.0 API), e.g. aliasing `typescript` to `npm:@typescript/typescript6` for library consumers while installing 7.0 under another name (such as `"@typescript/native": "npm:typescript@^7.0.2"`) to get the 7.0 `tsc`. A plan that only says "pin TypeScript 6" without explaining how both versions coexist fails."""),
        ],
    )


# ----------------------------------------------------------------------------- case 3: post-upgrade breakage

BROKEN_TSCONFIG = """{
  "compilerOptions": {
    "module": "nodenext",
    "moduleResolution": "nodenext",
    "outDir": "dist",
    "declaration": true
  },
  "include": ["src/**/*.ts"]
}
"""
BROKEN_TSCONFIG_TEST = """{
  "extends": "./tsconfig.json",
  "compilerOptions": { "noEmit": true },
  "include": ["src/**/*.ts", "test/**/*.ts"]
}
"""
BROKEN_LOG = """$ npx tsc -p tsconfig.json
src/server.ts:4:14 - error TS2580: Cannot find name 'process'. Do you need to install type definitions for node? Try `npm i --save-dev @types/node`.

4 const port = process.env.PORT ?? "8080";
               ~~~~~~~

Found 1 error in src/server.ts:4

$ npx tsc -p tsconfig.test.json
test/math.test.ts:3:1 - error TS2582: Cannot find name 'describe'. Do you need to install type definitions for a test runner? Try `npm i --save-dev @types/jest` or `npm i --save-dev @types/mocha`.

3 describe("add", () => {
  ~~~~~~~~

test/math.test.ts:4:3 - error TS2582: Cannot find name 'it'. Do you need to install type definitions for a test runner? Try `npm i --save-dev @types/jest` or `npm i --save-dev @types/mocha`.

4   it("adds", () => expect(add(1, 2)).toBe(3));
    ~~

src/server.ts:4:14 - error TS2580: Cannot find name 'process'. Do you need to install type definitions for node? Try `npm i --save-dev @types/node`.

Found 3 errors in 2 files.

$ git stash && npx -p typescript@5.7 tsc -p tsconfig.json && ls dist; git stash pop
math.d.ts  math.js  server.d.ts  server.js
$ npx tsc -p tsconfig.json; ls dist
src
$ ls dist/src
math.d.ts  math.js  server.d.ts  server.js
"""


def c_post_upgrade():
    case(
        "ts7-post-upgrade-breakage",
        ["ts7", "debugging"],
        """We bumped TypeScript from 5.7 to 7.0 and nothing else. Now tsc says it can't find `describe`, `it` and `process` even though @types/jest and @types/node are installed, and the build output moved — dist/ now contains a src/ folder (dist/src/server.js), so `node dist/server.js` fails. What changed and what's the right fix? The output of our CI run is in ci.log.""",
        {"tsconfig.json": BROKEN_TSCONFIG, "tsconfig.test.json": BROKEN_TSCONFIG_TEST, "ci.log": BROKEN_LOG,
         "package.json": {"name": "calc", "main": "dist/server.js", "devDependencies": {"typescript": "^7.0.2", "@types/jest": "^29.5.14", "@types/node": "^22.10.2"}},
         "src/math.ts": "export const add = (a: number, b: number) => a + b;\n",
         "src/server.ts": 'import { createServer } from "node:http";\nimport { add } from "./math.js";\n\nconst port = process.env.PORT ?? "8080";\ncreateServer((_q, r) => r.end(String(add(1, 2)))).listen(Number(port));\n',
         "test/math.test.ts": 'import { add } from "../src/math.js";\n\ndescribe("add", () => {\n  it("adds", () => expect(add(1, 2)).toBe(3));\n});\n'},
        """Two defaults changed in TypeScript 6.0 (kept in 7.0): `types` now defaults to [] (no automatic @types
inclusion) → list "types": ["node"] in tsconfig.json and ["node", "jest"] for the tests; `rootDir` now defaults to
the directory of tsconfig.json instead of being inferred from the inputs (src/) → set "rootDir": "./src" in
tsconfig.json (and override it, e.g. "rootDir": ".", in tsconfig.test.json) so output lands back in dist/server.js.""",
        [
            ("types-default", """The response explains that since TypeScript 6.0 (and in 7.0) the `types` compiler option defaults to an empty list, so installed @types packages (node, jest) are no longer included automatically, and fixes it by listing them, e.g. "types": ["node", "jest"]."""),
            ("rootdir-default", """The response explains that `rootDir` now defaults to the directory containing tsconfig.json (instead of being inferred as the common directory of the input files, which was src/), which is why output moved to dist/src, and fixes it with an explicit "rootDir": "./src" in tsconfig.json."""),
        ],
    )


CASES = [c_upgrade_service, c_tooling_plan, c_post_upgrade]

if __name__ == "__main__":
    for fn in CASES:
        fn()
        print("built", fn.__name__)
