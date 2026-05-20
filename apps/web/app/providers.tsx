"use client";

import { GoogleOAuthProvider } from "@react-oauth/google";
import {
  QueryClient,
  QueryClientProvider,
} from "@tanstack/react-query";
import { type ReactNode, useState } from "react";

export function Providers({ children }: { children: ReactNode }) {
  const [queryClient] = useState(() => new QueryClient());

  const googleClientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID;

  if (!googleClientId) {
    return (
      <QueryClientProvider client={queryClient}>
        <div className="flex min-h-screen items-center justify-center p-6">
          <div className="rounded-xl border bg-red-50 p-4 text-sm text-red-700">
            Missing NEXT_PUBLIC_GOOGLE_CLIENT_ID in apps/web/.env.local
          </div>
        </div>
      </QueryClientProvider>
    );
  }

  return (
    <QueryClientProvider client={queryClient}>
      <GoogleOAuthProvider clientId={googleClientId}>
        {children}
      </GoogleOAuthProvider>
    </QueryClientProvider>
  );
}