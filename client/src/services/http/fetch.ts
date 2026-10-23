import { environment } from "@config/environmentPublic";

export interface FetchClient {
  base(path: string, options?: RequestInit): Promise<Response>;
  get(path: string, options?: RequestInit): Promise<Response>;
  post(path: string, data: unknown, options?: RequestInit): Promise<Response>;
}

/** Resolve an API-relative path and preserve the native response and body stream. */
function base(path: string, options?: RequestInit): Promise<Response> {
  const url = `${environment.apiBaseUrl}/${path.replace(/^\/+/, "")}`;

  return globalThis.fetch(url, {
    credentials: "omit",
    ...options,
  });
}

const client: FetchClient = {
  base,

  get(path, options) {
    return base(path, {
      ...options,
      method: "GET",
    });
  },

  post(path, data, options) {
    const headers = new Headers(options?.headers);

    if (!headers.has("Content-Type")) {
      headers.set("Content-Type", "application/json");
    }

    return base(path, {
      ...options,
      method: "POST",
      headers,
      body: JSON.stringify(data),
    });
  },
};

export default client;
