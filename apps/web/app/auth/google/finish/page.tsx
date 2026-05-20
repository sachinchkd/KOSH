"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { setToken } from "@/lib/api";

const TEMP_TOKEN_KEY = "coop_tmp_token";

function getCookie(name: string) {
  const row = document.cookie
    .split("; ")
    .find((item) => item.startsWith(`${name}=`));

  return row ? decodeURIComponent(row.split("=")[1]) : null;
}

export default function GoogleFinishPage() {
  const router = useRouter();

  useEffect(() => {
    const token = getCookie(TEMP_TOKEN_KEY);

    if (!token) {
      router.replace("/login?error=missing_token");
      return;
    }

    setToken(token);

    document.cookie = `${TEMP_TOKEN_KEY}=; path=/; max-age=0; SameSite=Lax`;

    router.replace("/dashboard");
  }, [router]);

  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-950 p-4 text-white">
      Signing you in...
    </main>
  );
}