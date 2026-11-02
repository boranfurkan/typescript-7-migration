import * as express from "express";
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
