export interface Order {
  id: string;
  items: { sku: string; qty: number; price: number }[];
}

const store = new Map<string, Order>([
  ["o-1", { id: "o-1", items: [{ sku: "A", qty: 2, price: 9.5 }] }],
]);

export function listOrders(): Map<string, Order> {
  return store;
}
