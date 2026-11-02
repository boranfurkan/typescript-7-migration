import { add } from "../src/math.js";

describe("add", () => {
  it("adds", () => expect(add(1, 2)).toBe(3));
});
