const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api";

const TOKEN_KEY = "coop_token";

let token: string | null = null;

export function setToken(value: string | null) {
  token = value;

  if (typeof window === "undefined") return;

  if (value) {
    localStorage.setItem(TOKEN_KEY, value);
    document.cookie = `${TOKEN_KEY}=${encodeURIComponent(value)}; path=/; max-age=${
      60 * 60 * 24 * 7
    }; SameSite=Lax`;
  } else {
    localStorage.removeItem(TOKEN_KEY);
    document.cookie = `${TOKEN_KEY}=; path=/; max-age=0; SameSite=Lax`;
  }
}

export function getToken() {
  if (token) return token;

  if (typeof window !== "undefined") {
    token = localStorage.getItem(TOKEN_KEY);
  }

  return token;
}

export function clearToken() {
  setToken(null);
}

export function isLoggedIn() {
  return Boolean(getToken());
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

  const controller = new AbortController();

  const timeout = setTimeout(() => {
    controller.abort();
  }, 15000);

  try {
    const response = await fetch(`${API_URL}${path}`, {
      ...options,
      headers,
      signal: controller.signal,
    });

    const data = await response.json().catch(() => null);

    if (!response.ok) {
      if (response.status === 401 || response.status === 403) {
        clearToken();
      }

      const message = Array.isArray(data?.detail)
        ? data.detail.map((item: any) => item.msg).join(", ")
        : data?.detail || data?.message || "Request failed";

      throw new Error(message);
    }

    return data as T;
  } catch (err) {
    if (err instanceof DOMException && err.name === "AbortError") {
      throw new Error(
        "Backend request timed out. Check if the API server is running.",
      );
    }

    throw err;
  } finally {
    clearTimeout(timeout);
  }
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

  me: () => request<any>("/auth/me"),

  dashboard: () => request<any>("/dashboard/summary"),

  contributions: () => request<any[]>("/contributions"),

  createContribution: (formData: FormData) =>
    request<any>("/contributions", {
      method: "POST",
      body: formData,
    }),

  approveContribution: (id: string) =>
    request<any>(`/contributions/${id}/approve`, {
      method: "PATCH",
    }),

  rejectContribution: (id: string, remarks?: string) =>
    request<any>(`/contributions/${id}/reject`, {
      method: "PATCH",
      body: JSON.stringify({ remarks }),
    }),

  members: () => request<any[]>("/members"),

  createMember: (payload: {
    name: string;
    email: string;
    phone?: string;
    role?: string;
  }) =>
    request<any>("/members", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  monthlyReport: (month: string) =>
    request<any>(`/reports/monthly?month=${encodeURIComponent(month)}`),
};
