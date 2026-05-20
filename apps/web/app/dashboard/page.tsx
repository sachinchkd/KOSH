"use client";

import { useQuery } from "@tanstack/react-query";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { AppShell } from "@/components/app-shell";
import { StatCard } from "@/components/stat-card";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";
import { formatNpr } from "@/lib/utils";

export default function DashboardPage() {
  const { data, isLoading, error } = useQuery({ queryKey: ["dashboard"], queryFn: api.dashboard });

  return (
    <AppShell>
      <div className="mb-6">
        <h1 className="text-2xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-slate-500">Group saving summary and monthly status.</p>
      </div>

      {isLoading ? <p>Loading...</p> : null}
      {error ? <p className="text-red-600">{error instanceof Error ? error.message : "Failed to load dashboard"}</p> : null}

      {data ? (
        <>
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <StatCard title="Total Saved" value={formatNpr(data.total_saved)} helper="Approved contributions" />
            <StatCard title="This Month Collected" value={formatNpr(data.current_month_collected)} helper={`Expected ${formatNpr(data.current_month_expected)}`} />
            <StatCard title="Pending Amount" value={formatNpr(data.current_month_pending)} helper={`${data.pending_count} pending records`} />
            <StatCard title="Active Members" value={String(data.active_members)} helper="Member accounts" />
          </div>

          <div className="mt-6 grid gap-4 xl:grid-cols-3">
            <Card className="xl:col-span-2">
              <CardHeader>
                <CardTitle>Monthly Saving Chart</CardTitle>
                <CardDescription>Approved amount for recent months.</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={data.monthly_series}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="month" />
                      <YAxis />
                      <Tooltip formatter={(value) => formatNpr(Number(value))} />
                      <Bar dataKey="approved_amount" name="Approved" />
                      <Bar dataKey="pending_amount" name="Pending" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Unpaid This Month</CardTitle>
                <CardDescription>Members without approved payment.</CardDescription>
              </CardHeader>
              <CardContent>
                {data.unpaid_members.length === 0 ? (
                  <p className="text-sm text-slate-500">Everyone is paid or this view is member-only.</p>
                ) : (
                  <ul className="space-y-2">
                    {data.unpaid_members.map((name) => (
                      <li key={name} className="rounded-xl bg-slate-50 px-3 py-2 text-sm">{name}</li>
                    ))}
                  </ul>
                )}
              </CardContent>
            </Card>
          </div>
        </>
      ) : null}
    </AppShell>
  );
}
