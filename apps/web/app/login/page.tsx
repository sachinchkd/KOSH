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

    if (!response.credential) {
      setError("Google sign-in failed. No credential was returned.");
      return;
    }

    setLoading(true);

    try {
      const data = await api.googleLogin(response.credential);
      setToken(data.access_token);
      router.replace("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Google login failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-950 p-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>COOP Saving Login</CardTitle>
          <CardDescription>
            Sign in with your registered Gmail account.
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-4">
          <div className="flex justify-center">
            <GoogleLogin
              onSuccess={handleGoogleSuccess}
              onError={() => setError("Google sign-in was cancelled or failed.")}
              useOneTap
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
            Only Gmail accounts listed in the Google Sheet Members tab can access this app.
          </div>
        </CardContent>
      </Card>
    </main>
  );
}