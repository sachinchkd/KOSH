"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { getToken } from "@/lib/api";
import { useQuery } from "@tanstack/react-query";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { AppShell } from "@/components/app-shell";
import { StatCard } from "@/components/stat-card";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { api } from "@/lib/api";
import { formatNpr } from "@/lib/utils";

type MonthlySeriesItem = {
  month: string;
  approved_amount: number;
  pending_amount: number;
};

type DashboardResponse = {
  total_saved: number;
  current_month_collected: number;
  current_month_expected: number;
  current_month_pending: number;
  pending_count: number;
  active_members: number;
  unpaid_members: string[];
  monthly_series: MonthlySeriesItem[];
};

function safeMoney(value: unknown): number {
  const numberValue = Number(value);
  return Number.isFinite(numberValue) ? numberValue : 0;
}

export default function DashboardPage() {
  const { data, isLoading, error } = useQuery<DashboardResponse>({
    queryKey: ["dashboard"],
    queryFn: api.dashboard,
  });

  const dashboard = data
    ? {
        total_saved: safeMoney(data.total_saved),
        current_month_collected: safeMoney(data.current_month_collected),
        current_month_expected: safeMoney(data.current_month_expected),
        current_month_pending: safeMoney(data.current_month_pending),
        pending_count: Number(data.pending_count ?? 0),
        active_members: Number(data.active_members ?? 0),
        unpaid_members: Array.isArray(data.unpaid_members)
          ? data.unpaid_members
          : [],
        monthly_series: Array.isArray(data.monthly_series)
          ? data.monthly_series.map((item) => ({
              month: item.month,
              approved_amount: safeMoney(item.approved_amount),
              pending_amount: safeMoney(item.pending_amount),
            }))
          : [],
      }
    : null;

  return (
    <AppShell>
      <div className="mb-6">
        <h1 className="text-2xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-slate-500">
          Group saving summary fetched from Google Sheets.
        </p>
      </div>

      {isLoading ? <p>Loading dashboard...</p> : null}

      {error ? (
        <div className="rounded-xl bg-red-50 p-4 text-sm text-red-700">
          {error instanceof Error ? error.message : "Failed to load dashboard"}
        </div>
      ) : null}

      {dashboard ? (
        <>
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <StatCard
              title="Total Saved"
              value={formatNpr(dashboard.total_saved)}
              helper="Approved contributions"
            />

            <StatCard
              title="This Month Collected"
              value={formatNpr(dashboard.current_month_collected)}
              helper={`Expected ${formatNpr(dashboard.current_month_expected)}`}
            />

            <StatCard
              title="Pending Amount"
              value={formatNpr(dashboard.current_month_pending)}
              helper={`${dashboard.pending_count} pending records`}
            />

            <StatCard
              title="Active Members"
              value={String(dashboard.active_members)}
              helper="Member accounts"
            />
          </div>

          <div className="mt-6 grid gap-4 xl:grid-cols-3">
            <Card className="xl:col-span-2">
              <CardHeader>
                <CardTitle>Monthly Saving Chart</CardTitle>
                <CardDescription>
                  Approved and pending amounts from Google Sheets.
                </CardDescription>
              </CardHeader>

              <CardContent>
                <div className="h-80">
                  {dashboard.monthly_series.length === 0 ? (
                    <div className="flex h-full items-center justify-center rounded-xl bg-slate-50 text-sm text-slate-500">
                      No monthly contribution data yet.
                    </div>
                  ) : (
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={dashboard.monthly_series}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="month" />
                        <YAxis />
                        <Tooltip
                          formatter={(value) => formatNpr(Number(value))}
                        />
                        <Bar dataKey="approved_amount" name="Approved" />
                        <Bar dataKey="pending_amount" name="Pending" />
                      </BarChart>
                    </ResponsiveContainer>
                  )}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Unpaid This Month</CardTitle>
                <CardDescription>
                  Members without approved payment this month.
                </CardDescription>
              </CardHeader>

              <CardContent>
                {dashboard.unpaid_members.length === 0 ? (
                  <p className="text-sm text-slate-500">
                    Everyone is paid for this month.
                  </p>
                ) : (
                  <ul className="space-y-2">
                    {dashboard.unpaid_members.map((name) => (
                      <li
                        key={name}
                        className="rounded-xl bg-slate-50 px-3 py-2 text-sm"
                      >
                        {name}
                      </li>
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