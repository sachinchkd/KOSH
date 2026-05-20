import type { Contribution, DashboardSummary, Member, User } from "@/lib/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export function getToken() {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("coop_token");
}

export function setToken(token: string) {
  localStorage.setItem("coop_token", token);
}

export function clearToken() {
  localStorage.removeItem("coop_token");
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers = new Headers(options.headers);

  if (!(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers
  });

  if (!response.ok) {
    let message = "Request failed";
    try {
      const data = await response.json();
      message = data.detail || message;
    } catch {
      // keep fallback message
    }
    throw new Error(message);
  }

  return response.json();
}

export const api = {
  async login(email: string, password: string) {
    return request<{ access_token: string; token_type: string }>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password })
    });
  },

  async me() {
    return request<User>("/auth/me");
  },

  async dashboard() {
    return request<DashboardSummary>("/dashboard/summary");
  },

  async members() {
    return request<Member[]>("/members");
  },

  async createMember(payload: { name: string; email: string; phone?: string; password: string; role: string }) {
    return request<Member>("/members", {
      method: "POST",
      body: JSON.stringify(payload)
    });
  },

  async contributions(params?: { status_filter?: string; month?: string; member_id?: string }) {
    const search = new URLSearchParams();
    if (params?.status_filter) search.set("status_filter", params.status_filter);
    if (params?.month) search.set("month", params.month);
    if (params?.member_id) search.set("member_id", params.member_id);
    const query = search.toString();
    return request<Contribution[]>(`/contributions${query ? `?${query}` : ""}`);
  },

  async createContribution(form: FormData) {
    return request<Contribution>("/contributions", {
      method: "POST",
      body: form
    });
  },

  async approveContribution(id: number, remarks?: string) {
    return request<Contribution>(`/contributions/${id}/approve`, {
      method: "PATCH",
      body: JSON.stringify({ remarks })
    });
  },

  async rejectContribution(id: number, remarks?: string) {
    return request<Contribution>(`/contributions/${id}/reject`, {
      method: "PATCH",
      body: JSON.stringify({ remarks })
    });
  },

  async monthlyReport(month: string) {
    return request<{
      month: string;
      approved: number;
      pending: number;
      rejected: number;
      rows: Contribution[];
    }>(`/reports/monthly?month=${month}`);
  }
};
