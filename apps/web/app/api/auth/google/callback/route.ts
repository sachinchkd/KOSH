import { NextRequest, NextResponse } from "next/server";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api";

const TEMP_TOKEN_KEY = "coop_tmp_token";

export async function POST(req: NextRequest) {
  const formData = await req.formData();
  const credential = formData.get("credential");

  const baseUrl = new URL(req.url).origin;

  if (!credential || typeof credential !== "string") {
    return NextResponse.redirect(
      `${baseUrl}/login?error=missing_google_credential`
    );
  }

  try {
    const backendRes = await fetch(`${API_URL}/auth/google`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ credential }),
    });

    const data = await backendRes.json().catch(() => null);

    if (!backendRes.ok) {
      console.error("Backend Google login failed:", data);

      return NextResponse.redirect(
        `${baseUrl}/login?error=backend_login_failed`
      );
    }

    if (!data?.access_token) {
      return NextResponse.redirect(`${baseUrl}/login?error=no_access_token`);
    }

    const res = NextResponse.redirect(`${baseUrl}/auth/google/finish`);

    res.cookies.set(TEMP_TOKEN_KEY, data.access_token, {
      path: "/",
      maxAge: 60,
      sameSite: "lax",
      secure: process.env.NODE_ENV === "production",
      httpOnly: false,
    });

    return res;
  } catch (error) {
    console.error("Google callback error:", error);

    return NextResponse.redirect(`${baseUrl}/login?error=server_error`);
  }
}