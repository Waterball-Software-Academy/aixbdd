import type { ZodTypeAny } from "zod";

export interface OperationDescriptor {
  operationId: string;
  method: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
  // OpenAPI-style path template, e.g. "/orders/{id}". Path variables are
  // matched as `[^/]+` segments by the fixture (no schema-typed coercion).
  pathTemplate: string;
  // Zod schema imported from `./_generated`. Omit when the operation has no
  // request body / response body in openapi.yml.
  requestSchema?: ZodTypeAny;
  responseSchema?: ZodTypeAny;
  // Happy-path response builder. Receives the closure store, the parsed
  // request body, and parsed URL search params. Must return a value that
  // conforms to `responseSchema`. Keep this pure — no I/O, no Date.now() in
  // domain payload (use the fixture clock fixture if you need time).
  defaultHandler: (ctx: {
    store: Map<string, unknown[]>;
    body: unknown;
    query: URLSearchParams;
    pathParams: Record<string, string>;
  }) => unknown;
}

// Worker fills this during pre-red §3.2:
//   1. Read `${CONTRACTS_DIR}/api.yml`.
//   2. For each path × method with an `operationId`, add one entry below.
//   3. Wire `requestSchema` / `responseSchema` to exports from `./_generated`.
//   4. Write a minimal `defaultHandler` that reads from `store` (seeded via
//      `mockApi.seed(...)`) and returns the happy-path shape.
//
// Example (DO NOT keep in real boundary — illustrative only):
//
//   import { CreateRoomRequest, CreateRoomResponse } from "./_generated";
//
//   export const operationRegistry: Record<string, OperationDescriptor> = {
//     createRoom: {
//       operationId: "createRoom",
//       method: "POST",
//       pathTemplate: "/rooms",
//       requestSchema: CreateRoomRequest,
//       responseSchema: CreateRoomResponse,
//       defaultHandler: ({ store, body }) => {
//         const input = body as { roomCode: string; capacity: number };
//         const rooms = (store.get("rooms") ?? []) as Array<{ roomCode: string; capacity: number }>;
//         rooms.push({ roomCode: input.roomCode, capacity: input.capacity });
//         store.set("rooms", rooms);
//         return { roomCode: input.roomCode, capacity: input.capacity, seatsTaken: 0 };
//       },
//     },
//   };
export const operationRegistry: Record<string, OperationDescriptor> = {};
