"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { type FormEvent, useState } from "react";
import { AppShell } from "@/components/app-shell";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import { Table, TBody, TD, TH, THead, TR } from "@/components/ui/table";
import { api } from "@/lib/api";
import { formatNpr } from "@/lib/utils";

export default function MembersPage() {
  const queryClient = useQueryClient();
  const { data, isLoading, error } = useQuery({
    queryKey: ["members"],
    queryFn: api.members,
  });
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");

  const [role, setRole] = useState("member");
  const [formError, setFormError] = useState<string | null>(null);

  const createMember = useMutation({
    mutationFn: () => api.createMember({ name, email, phone, role }),
    onSuccess: () => {
      setName("");
      setEmail("");
      setPhone("");
      queryClient.invalidateQueries({ queryKey: ["members"] });
    },
    onError: (err) =>
      setFormError(
        err instanceof Error ? err.message : "Could not create member",
      ),
  });

  function submit(event: FormEvent) {
    event.preventDefault();
    setFormError(null);
    createMember.mutate();
  }

  return (
    <AppShell>
      <div className="mb-6">
        <h1 className="text-2xl font-bold tracking-tight">Members</h1>
        <p className="text-slate-500">
          Manage the eight KOSH members and admins.
        </p>
      </div>

      <div className="grid gap-6 xl:grid-cols-3">
        <Card className="xl:col-span-2">
          <CardHeader>
            <CardTitle>Member List</CardTitle>
            <CardDescription>
              Total paid means approved contributions.
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
                  <TH>Name</TH>
                  <TH>Email</TH>
                  <TH>Phone</TH>
                  <TH>Role</TH>
                  <TH>Total Paid</TH>
                </TR>
              </THead>
              <TBody>
                {data?.map((member) => (
                  <TR key={member.id}>
                    <TD>{member.name}</TD>
                    <TD>{member.email}</TD>
                    <TD>{member.phone || "-"}</TD>
                    <TD>{member.role}</TD>
                    <TD>{formatNpr(member.total_paid)}</TD>
                  </TR>
                ))}
              </TBody>
            </Table>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Add Member</CardTitle>
            <CardDescription>Admin-only action.</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={submit} className="space-y-4">
              <div className="space-y-2">
                <Label>Name</Label>
                <Input
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label>Email</Label>
                <Input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label>Phone</Label>
                <Input
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label>Role</Label>
                <Select value={role} onChange={(e) => setRole(e.target.value)}>
                  <option value="member">member</option>
                  <option value="admin">admin</option>
                </Select>
              </div>
              {formError ? (
                <div className="rounded-xl bg-red-50 p-3 text-sm text-red-700">
                  {formError}
                </div>
              ) : null}
              <Button disabled={createMember.isPending}>
                {createMember.isPending ? "Creating..." : "Create Member"}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}
