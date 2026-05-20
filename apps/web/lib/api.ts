const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

let token: string | null = null;

export function setToken(value: string | null) {
  token = value;

  if (typeof window !== "undefined") {
    if (value) {
      localStorage.setItem("coop_token", value);
      document.cookie = `coop_token=${value}; path=/; max-age=${60 * 60 * 24 * 7}; SameSite=Lax`;
    } else {
      localStorage.removeItem("coop_token");
      document.cookie = "coop_token=; path=/; max-age=0; SameSite=Lax";
    }
  }
}

export function getToken() {
  if (token) return token;

  if (typeof window !== "undefined") {
    token = localStorage.getItem("coop_token");
  }

  return token;
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers);

  if (!(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }

  const authToken = getToken();

  if (authToken) {
    headers.set("Authorization", `Bearer ${authToken}`);
  }

  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers,
  });

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    throw new Error(data?.detail || "Request failed");
  }

  return data as T;
}

export type TokenResponse = {
  access_token: string;
  token_type: string;
};

export const api = {
  googleLogin: (credential: string) =>
    request<TokenResponse>("/auth/google", {
      method: "POST",
      body: JSON.stringify({ credential }),
    }),

  dashboard: () => request<any>("/dashboard/summary"),

  me: () => request<any>("/auth/me"),
};