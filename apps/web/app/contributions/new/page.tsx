"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { type FormEvent, useState } from "react";
import { AppShell } from "@/components/app-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { api } from "@/lib/api";
import { currentMonth } from "@/lib/utils";

export default function NewContributionPage() {
  const router = useRouter();
  const [memberId, setMemberId] = useState("");
  const [month, setMonth] = useState(currentMonth());
  const [amount, setAmount] = useState("1000");
  const [paymentMethod, setPaymentMethod] = useState("Cash");
  const [remarks, setRemarks] = useState("");
  const [photo, setPhoto] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);

  const { data: members } = useQuery({ queryKey: ["members"], queryFn: api.members });

  const mutation = useMutation({
    mutationFn: async () => {
      const form = new FormData();
      if (memberId) form.set("member_id", memberId);
      form.set("month", month);
      form.set("amount", amount);
      form.set("payment_method", paymentMethod);
      if (remarks) form.set("remarks", remarks);
      if (photo) form.set("photo", photo);
      return api.createContribution(form);
    },
    onSuccess: () => router.push("/contributions"),
    onError: (err) => setError(err instanceof Error ? err.message : "Could not save contribution")
  });

  function onSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    mutation.mutate();
  }

  return (
    <AppShell>
      <div className="mb-6">
        <h1 className="text-2xl font-bold tracking-tight">Add Monthly Saving</h1>
        <p className="text-slate-500">Submit NPR 1000 saving with optional receipt/photo.</p>
      </div>

      <Card className="max-w-2xl">
        <CardHeader>
          <CardTitle>Saving Entry</CardTitle>
          <CardDescription>Record a payment for a month.</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={onSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label>Member</Label>
              <Select value={memberId} onChange={(e) => setMemberId(e.target.value)}>
                <option value="">Current logged-in member</option>
                {members?.filter((m) => m.role === "member").map((member) => (
                  <option key={member.id} value={member.id}>{member.name}</option>
                ))}
              </Select>
              <p className="text-xs text-slate-500">Only admins can submit on behalf of another member.</p>
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label>Month</Label>
                <Input type="month" value={month} onChange={(e) => setMonth(e.target.value)} required />
              </div>
              <div className="space-y-2">
                <Label>Amount</Label>
                <Input type="number" value={amount} onChange={(e) => setAmount(e.target.value)} required />
              </div>
            </div>

            <div className="space-y-2">
              <Label>Payment Method</Label>
              <Select value={paymentMethod} onChange={(e) => setPaymentMethod(e.target.value)}>
                <option>Cash</option>
                <option>Bank Transfer</option>
                <option>eSewa</option>
                <option>Khalti</option>
                <option>Other</option>
              </Select>
            </div>

            <div className="space-y-2">
              <Label>Receipt / Photo</Label>
              <Input type="file" accept="image/*,.pdf" onChange={(e) => setPhoto(e.target.files?.[0] || null)} />
            </div>

            <div className="space-y-2">
              <Label>Remarks</Label>
              <Textarea value={remarks} onChange={(e) => setRemarks(e.target.value)} placeholder="Optional note" />
            </div>

            {error ? <div className="rounded-xl bg-red-50 p-3 text-sm text-red-700">{error}</div> : null}

            <Button disabled={mutation.isPending}>{mutation.isPending ? "Saving..." : "Submit Saving"}</Button>
          </form>
        </CardContent>
      </Card>
    </AppShell>
  );
}
