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

type MonthlyReportRow = {
  id: string;
  member_name: string;
  amount: number;
  status: string;
  month?: string;
  payment?: string;
  payment_method?: string;
  submitted_at?: string;
  approved_at?: string;
  approved_by?: string;
  remarks?: string;
  url?: string;
  photo_url?: string;
};

type MonthlyReportData = {
  month: string;
  rows: MonthlyReportRow[];
  total_amount?: number;
  approved_amount?: number;
  pending_amount?: number;
  rejected_amount?: number;
};

export default function MonthlyReportPage() {
  const [month, setMonth] = useState(currentMonth());

  const { data, isLoading, error } = useQuery<MonthlyReportData>({
    queryKey: ["monthly-report", month],
    queryFn: () => api.monthlyReport(month),
  });

  return (
    <AppShell>
      <div className="mb-6">
        <h1 className="text-2xl font-bold tracking-tight">Monthly Report</h1>
        <p className="text-slate-500">Review contribution status by month.</p>
      </div>

      <div className="mb-6 max-w-xs space-y-2">
        <Label>Month</Label>
        <Input
          type="month"
          value={month}
          onChange={(e) => setMonth(e.target.value)}
        />
      </div>

      {isLoading ? <p>Loading...</p> : null}

      {error ? (
        <p className="text-red-600">
          {error instanceof Error ? error.message : "Failed to load"}
        </p>
      ) : null}

      {data ? (
        <>
          <div className="mb-6 grid gap-4 md:grid-cols-3">
            <StatCard
              title="Approved"
              value={formatNpr(data.approved_amount ?? 0)}
            />
            <StatCard
              title="Pending"
              value={formatNpr(data.pending_amount ?? 0)}
            />
            <StatCard
              title="Rejected"
              value={formatNpr(data.rejected_amount ?? 0)}
            />
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
                  {data.rows.map((row) => {
                    const receiptUrl = row.photo_url || row.url;
                    const paymentMethod = row.payment_method || row.payment || "-";
                    const submittedDate = row.submitted_at
                      ? new Date(row.submitted_at).toLocaleDateString()
                      : "-";

                    return (
                      <TR key={row.id}>
                        <TD>{row.member_name}</TD>
                        <TD>{formatNpr(row.amount)}</TD>
                        <TD>{paymentMethod}</TD>
                        <TD>
                          <StatusBadge status={row.status || "Pending"} />
                        </TD>
                        <TD>{submittedDate}</TD>
                        <TD>
                          {receiptUrl ? (
                            <a
                              className="underline"
                              href={receiptUrl}
                              target="_blank"
                              rel="noreferrer"
                            >
                              View
                            </a>
                          ) : (
                            "-"
                          )}
                        </TD>
                      </TR>
                    );
                  })}
                </TBody>
              </Table>
            </CardContent>
          </Card>
        </>
      ) : null}
    </AppShell>
  );
}