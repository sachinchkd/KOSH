import { NextResponse, type NextRequest } from "next/server";

const TOKEN_KEY = "coop_token";

const protectedRoutes = [
  "/dashboard",
  "/members",
  "/contributions",
  "/reports",
  "/settings",
];

export function middleware(request: NextRequest) {
  const pathname = request.nextUrl.pathname;
  const token = request.cookies.get(TOKEN_KEY)?.value;

  const isProtectedRoute = protectedRoutes.some((route) =>
    pathname === route || pathname.startsWith(`${route}/`)
  );

  if (pathname === "/") {
    return NextResponse.redirect(
      new URL(token ? "/dashboard" : "/login", request.url)
    );
  }

  if (pathname === "/login" && token) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  if (isProtectedRoute && !token) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    "/",
    "/login",
    "/dashboard/:path*",
    "/members/:path*",
    "/contributions/:path*",
    "/reports/:path*",
    "/settings/:path*",
  ],
};