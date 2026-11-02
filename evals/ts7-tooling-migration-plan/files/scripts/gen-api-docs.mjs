import ts from "typescript";

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
