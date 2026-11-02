export function getCart(id: string): Promise<unknown> {
  return fetch(`/api/cart/${id}`).then((r) => r.json());
}
