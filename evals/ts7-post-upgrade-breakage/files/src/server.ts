import { createServer } from "node:http";
import { add } from "./math.js";

const port = process.env.PORT ?? "8080";
createServer((_q, r) => r.end(String(add(1, 2)))).listen(Number(port));
