"use client";

import { AppShell } from "@/components/app-shell";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function SettingsPage() {
  return (
    <AppShell>
      <div className="mb-6">
        <h1 className="text-2xl font-bold tracking-tight">Settings</h1>
        <p className="text-slate-500">Environment and Google integration notes.</p>
      </div>

      <Card className="max-w-3xl">
        <CardHeader>
          <CardTitle>App Settings</CardTitle>
          <CardDescription>Configure backend environment variables in apps/api/.env.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4 text-sm text-slate-600">
          <div className="rounded-2xl bg-slate-50 p-4">
            <div className="font-semibold text-slate-900">Monthly Amount</div>
            <div>Set <code>MONTHLY_SAVING_AMOUNT=1000</code> in the backend env.</div>
          </div>
          <div className="rounded-2xl bg-slate-50 p-4">
            <div className="font-semibold text-slate-900">Google Sheets</div>
            <div>Set <code>GOOGLE_ENABLED=true</code>, <code>GOOGLE_SHEET_ID</code>, and service account credentials.</div>
          </div>
          <div className="rounded-2xl bg-slate-50 p-4">
            <div className="font-semibold text-slate-900">Photos</div>
            <div>Local uploads work by default. Google Drive upload works when <code>GOOGLE_DRIVE_FOLDER_ID</code> is configured.</div>
          </div>
        </CardContent>
      </Card>
    </AppShell>
  );
}
