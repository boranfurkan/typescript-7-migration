import { listOrders } from "../src/orders";

describe("listOrders", () => {
  it("returns the seeded order", () => {
    expect(listOrders().get("o-1")?.items.length).toBe(1);
  });
});
