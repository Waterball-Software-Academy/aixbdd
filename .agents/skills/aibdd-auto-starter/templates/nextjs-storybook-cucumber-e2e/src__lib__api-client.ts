import { z } from "zod";

import { env } from "./env";

export class ApiError extends Error {
  readonly status: number;
  readonly url: string;
  readonly body: unknown;

  constructor(message: string, status: number, url: string, body: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.url = url;
    this.body = body;
  }
}

interface RequestOptions<TSchema extends z.ZodTypeAny> {
  method?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
  body?: unknown;
  schema: TSchema;
  headers?: Record<string, string>;
  next?: { revalidate?: number; tags?: string[] };
  cache?: RequestCache;
  signal?: AbortSignal;
}

const isServer = typeof window === "undefined";

function resolveBaseUrl(): string {
  return isServer ? env.API_BASE_URL : env.NEXT_PUBLIC_API_BASE_URL;
}

export async function apiFetch<TSchema extends z.ZodTypeAny>(
  path: string,
  { method = "GET", body, schema, headers, next, cache, signal }: RequestOptions<TSchema>,
): Promise<z.infer<TSchema>> {
  const url = new URL(path, resolveBaseUrl()).toString();

  const finalHeaders: Record<string, string> = {
    Accept: "application/json",
    ...headers,
  };
  if (body !== undefined) finalHeaders["Content-Type"] = "application/json";
  if (isServer && env.API_TOKEN) {
    finalHeaders["Authorization"] = `Bearer ${env.API_TOKEN}`;
  }

  const response = await fetch(url, {
    method,
    headers: finalHeaders,
    body: body !== undefined ? JSON.stringify(body) : undefined,
    next,
    cache,
    signal,
  });

  const text = await response.text();
  const json = text.length > 0 ? safeJsonParse(text) : null;

  if (!response.ok) {
    throw new ApiError(
      `Request failed: ${response.status} ${response.statusText}`,
      response.status,
      url,
      json,
    );
  }

  const parsed = schema.safeParse(json);
  if (!parsed.success) {
    throw new ApiError(
      "Response failed schema validation",
      response.status,
      url,
      parsed.error.flatten(),
    );
  }
  return parsed.data;
}

function safeJsonParse(text: string): unknown {
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}
