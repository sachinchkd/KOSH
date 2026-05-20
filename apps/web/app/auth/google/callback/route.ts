import { NextRequest, NextResponse } from "next/server";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api";

const TEMP_TOKEN_KEY = "coop_tmp_token";

function redirectGet(url: string) {
  return NextResponse.redirect(url, { status: 303 });
}

// Optional test route
export async function GET() {
  return NextResponse.json({
    ok: true,
    message: "Google callback route exists. Google should POST here.",
  });
}

export async function POST(req: NextRequest) {
  const formData = await req.formData();
  const credential = formData.get("credential");

  const baseUrl = new URL(req.url).origin;

  if (!credential || typeof credential !== "string") {
    return redirectGet(`${baseUrl}/login?error=missing_google_credential`);
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

    if (!backendRes.ok || !data?.access_token) {
      return redirectGet(`${baseUrl}/login?error=backend_login_failed`);
    }

    const res = redirectGet(`${baseUrl}/auth/google/finish`);

    res.cookies.set(TEMP_TOKEN_KEY, data.access_token, {
      path: "/",
      maxAge: 60,
      sameSite: "lax",
      secure: true,
      httpOnly: false,
    });

    return res;
  } catch (error) {
    console.error("Google callback error:", error);
    return redirectGet(`${baseUrl}/login?error=server_error`);
  }
}