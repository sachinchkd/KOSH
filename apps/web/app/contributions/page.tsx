"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { AppShell } from "@/components/app-shell";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { StatusBadge } from "@/components/ui/badge";
import { Table, TBody, TD, TH, THead, TR } from "@/components/ui/table";
import { api } from "@/lib/api";
import { cn, formatNpr } from "@/lib/utils";

export default function ContributionsPage() {
  const queryClient = useQueryClient();
  const { data, isLoading, error } = useQuery({
    queryKey: ["contributions"],
    queryFn: () => api.contributions(),
  });

  const approve = useMutation({
    mutationFn: (id: string) => api.approveContribution(id),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: ["contributions"] }),
  });
  const reject = useMutation({
    mutationFn: ({ id, remarks }: { id: string; remarks?: string }) =>
      api.rejectContribution(id, remarks),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: ["contributions"] }),
  });

  return (
    <AppShell>
      <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Contributions</h1>
          <p className="text-slate-500">Monthly savings and approval status.</p>
        </div>
        <Link
          href="/contributions/new"
          className={cn(
            "inline-flex items-center justify-center rounded-xl bg-slate-950 px-4 py-2 text-sm font-medium text-white transition hover:bg-slate-800",
          )}
        >
          Add Saving
        </Link>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>All Records</CardTitle>
          <CardDescription>
            Admins can approve or reject pending records.
          </CardDescription>
        </CardHeader>
        <CardContent className="overflow-x-auto p-0">
          {isLoading ? <p className="p-5">Loading...</p> : null}
          {error ? (
            <p className="p-5 text-red-600">
              {error instanceof Error ? error.message : "Failed to load"}
            </p>
          ) : null}
          <Table>
            <THead>
              <TR>
                <TH>Member</TH>
                <TH>Month</TH>
                <TH>Amount</TH>
                <TH>Method</TH>
                <TH>Status</TH>
                <TH>Receipt</TH>
                <TH>Action</TH>
              </TR>
            </THead>
            <TBody>
              {data?.map((item) => (
                <TR key={item.id}>
                  <TD>{item.member_name}</TD>
                  <TD>{item.month}</TD>
                  <TD>{formatNpr(item.amount)}</TD>
                  <TD>{item.payment_method}</TD>
                  <TD>
                    <StatusBadge status={item.status} />
                  </TD>
                  <TD>
                    {item.photo_url ? (
                      <a
                        className="text-sm font-medium text-slate-900 underline"
                        href={item.photo_url}
                        target="_blank"
                      >
                        View
                      </a>
                    ) : (
                      <span className="text-slate-400">No photo</span>
                    )}
                  </TD>
                  <TD>
                    {item.status === "pending" ? (
                      <div className="flex gap-2">
                        <Button
                          className="h-8 px-3"
                          onClick={() => approve.mutate(item.id)}
                        >
                          Approve
                        </Button>
                        <Button
                          className="h-8 px-3"
                          variant="destructive"
                          onClick={() => reject.mutate(item.id)}
                        >
                          Reject
                        </Button>
                      </div>
                    ) : (
                      <span className="text-slate-400">Done</span>
                    )}
                  </TD>
                </TR>
              ))}
            </TBody>
          </Table>
        </CardContent>
      </Card>
    </AppShell>
  );
}
