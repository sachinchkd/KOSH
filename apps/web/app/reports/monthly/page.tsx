"use client";

import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { AppShell } from "@/components/app-shell";
import { StatCard } from "@/components/stat-card";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { StatusBadge } from "@/components/ui/badge";
import { Table, TBody, TD, TH, THead, TR } from "@/components/ui/table";
import { api } from "@/lib/api";
import { currentMonth, formatNpr } from "@/lib/utils";

export default function MonthlyReportPage() {
  const [month, setMonth] = useState(currentMonth());
  const { data, isLoading, error } = useQuery({ queryKey: ["monthly-report", month], queryFn: () => api.monthlyReport(month) });

  return (
    <AppShell>
      <div className="mb-6">
        <h1 className="text-2xl font-bold tracking-tight">Monthly Report</h1>
        <p className="text-slate-500">Review contribution status by month.</p>
      </div>

      <div className="mb-6 max-w-xs space-y-2">
        <Label>Month</Label>
        <Input type="month" value={month} onChange={(e) => setMonth(e.target.value)} />
      </div>

      {isLoading ? <p>Loading...</p> : null}
      {error ? <p className="text-red-600">{error instanceof Error ? error.message : "Failed to load"}</p> : null}

      {data ? (
        <>
          <div className="mb-6 grid gap-4 md:grid-cols-3">
            <StatCard title="Approved" value={formatNpr(data.approved)} />
            <StatCard title="Pending" value={formatNpr(data.pending)} />
            <StatCard title="Rejected" value={formatNpr(data.rejected)} />
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Rows</CardTitle>
            </CardHeader>
            <CardContent className="overflow-x-auto p-0">
              <Table>
                <THead>
                  <TR>
                    <TH>Member</TH>
                    <TH>Amount</TH>
                    <TH>Method</TH>
                    <TH>Status</TH>
                    <TH>Submitted</TH>
                    <TH>Receipt</TH>
                  </TR>
                </THead>
                <TBody>
                  {data.rows.map((row) => (
                    <TR key={row.id}>
                      <TD>{row.member_name}</TD>
                      <TD>{formatNpr(row.amount)}</TD>
                      <TD>{row.payment_method}</TD>
                      <TD><StatusBadge status={row.status} /></TD>
                      <TD>{new Date(row.submitted_at).toLocaleDateString()}</TD>
                      <TD>{row.photo_url ? <a className="underline" href={row.photo_url} target="_blank">View</a> : "-"}</TD>
                    </TR>
                  ))}
                </TBody>
              </Table>
            </CardContent>
          </Card>
        </>
      ) : null}
    </AppShell>
  );
}
