import { z } from "zod";

const serverSchema = z.object({
  NODE_ENV: z.enum(["development", "test", "production"]).default("development"),
  API_BASE_URL: z.string().url().default("http://localhost:4000"),
  API_TOKEN: z.string().min(1).optional(),
});

const clientSchema = z.object({
  NEXT_PUBLIC_API_BASE_URL: z.string().url().default("http://localhost:4000"),
});

const isServer = typeof window === "undefined";

const parsedServer = isServer
  ? serverSchema.safeParse(process.env)
  : { success: true as const, data: serverSchema.parse({}) };

const parsedClient = clientSchema.safeParse({
  NEXT_PUBLIC_API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL,
});

if (!parsedServer.success) {
  console.error("Invalid server env:", parsedServer.error.flatten().fieldErrors);
  throw new Error("Invalid server environment variables");
}
if (!parsedClient.success) {
  console.error("Invalid client env:", parsedClient.error.flatten().fieldErrors);
  throw new Error("Invalid client environment variables");
}

export const env = {
  ...parsedServer.data,
  ...parsedClient.data,
} as const;

export type Env = typeof env;
