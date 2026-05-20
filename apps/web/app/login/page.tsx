"use client";

import { GoogleLogin, type CredentialResponse } from "@react-oauth/google";
import { useRouter } from "next/navigation";
import { useState } from "react";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { api, setToken } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleGoogleSuccess(response: CredentialResponse) {
    setError(null);

    console.log("Google response:", response);

    if (!response.credential) {
      setError("Google sign-in failed. No credential was returned.");
      return;
    }

    setLoading(true);

    try {
      console.log("Calling backend /auth/google...");
      const data = await api.googleLogin(response.credential);
      console.log("Backend response:", data);

      if (!data?.access_token) {
        throw new Error("Backend did not return access_token");
      }

      setToken(data.access_token);
      router.replace("/dashboard");
    } catch (err) {
      console.error("Login failed:", err);
      setError(err instanceof Error ? err.message : "Google login failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-950 p-4">
      <Card className="w-full max-w-md text-center text-lg">
        <CardHeader>
          <CardTitle>KOSH v1.0 Saving Login</CardTitle>
          <CardDescription>
            Sign in with your registered Gmail account.
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-4">
          <div className="flex justify-center">
            <GoogleLogin
              onSuccess={handleGoogleSuccess}
              size="large"
              text="signin_with"
              shape="rectangular"
              logo_alignment="left"
              ux_mode="redirect"
              login_uri="https://kosh-web-chi.vercel.app/auth/google/callback"
              onError={() =>
                setError("Google sign-in was cancelled or failed.")
              }
              useOneTap={false}
              use_fedcm_for_prompt={false}
            />
          </div>

          {loading ? (
            <div className="rounded-xl bg-slate-50 p-3 text-sm text-slate-600">
              Signing you in...
            </div>
          ) : null}

          {error ? (
            <div className="rounded-xl bg-red-50 p-3 text-sm text-red-700">
              {error}
            </div>
          ) : null}

          <div className="rounded-xl bg-slate-50 p-3 text-xs text-slate-500">
            This release is intended for initial testing and feedback. Core
            features are functional, but improvements may be made as the system
            is used by members and admins.
          </div>
        </CardContent>
      </Card>
    </main>
  );
}
