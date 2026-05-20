"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import {
  LayoutDashboard,
  LogOut,
  PlusCircle,
  ReceiptText,
  Settings,
  Users,
  BarChart3,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { api, clearToken, getToken } from "@/lib/api";
import type { User } from "@/lib/types";
import { cn } from "@/lib/utils";

const nav = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/contributions/new", label: "New Saving", icon: PlusCircle },
  { href: "/contributions", label: "Contributions", icon: ReceiptText },
  { href: "/members", label: "Members", icon: Users },
  { href: "/reports/monthly", label: "Reports", icon: BarChart3 },
  { href: "/settings", label: "Settings", icon: Settings },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();

  const [user, setUser] = useState<User | null>(null);
  const [checkingAuth, setCheckingAuth] = useState(true);

  useEffect(() => {
    async function checkAuth() {
      const token = getToken();

      if (!token) {
        router.replace("/login");
        return;
      }

      try {
        const currentUser = await api.me();
        setUser(currentUser);
        setCheckingAuth(false);
      } catch {
        clearToken();
        router.replace("/login");
      }
    }

    checkAuth();
  }, [router]);

  function logout() {
    clearToken();
    router.replace("/login");
  }

  if (checkingAuth) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-50">
        <div className="rounded-xl bg-white px-5 py-4 text-sm text-slate-600 shadow">
          Checking login...
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <aside className="fixed inset-y-0 left-0 hidden w-72 border-r border-slate-200 bg-white p-5 lg:block">
        <Link
          href="/dashboard"
          className="block rounded-2xl bg-slate-950 p-4 text-white"
        >
          <div className="text-lg font-bold">KOSH Saving v1.0</div>
          <div className="text-sm text-slate-300">
            Monthly saving
          </div>
        </Link>

        <nav className="mt-6 space-y-1">
          {nav.map((item) => {
            const Icon = item.icon;
            const active = pathname === item.href;

            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100",
                  active && "bg-slate-100 text-slate-950"
                )}
              >
                <Icon className="h-4 w-4" />
                {item.label}
              </Link>
            );
          })}
        </nav>

        <div className="absolute bottom-5 left-5 right-5 rounded-2xl border border-slate-200 p-4">
          <div className="text-sm font-semibold">{user?.name}</div>
          <div className="text-xs text-slate-500">{user?.role}</div>

          <Button variant="outline" className="mt-3 w-full" onClick={logout}>
            <LogOut className="mr-2 h-4 w-4" />
            Logout
          </Button>
        </div>
      </aside>

      <main className="lg:pl-72">
        <div className="border-b border-slate-200 bg-white p-4 lg:hidden">
          <div className="flex items-center justify-between">
            <Link href="/dashboard" className="font-bold">
              KOSH Saving v1.0
            </Link>

            <Button variant="outline" onClick={logout}>
              Logout
            </Button>
          </div>

          <div className="mt-3 flex gap-2 overflow-x-auto pb-1">
            {nav.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="whitespace-nowrap rounded-full bg-slate-100 px-3 py-1.5 text-xs font-medium"
              >
                {item.label}
              </Link>
            ))}
          </div>
        </div>

        <div className="p-4 sm:p-6 lg:p-8">{children}</div>
      </main>
    </div>
  );
}