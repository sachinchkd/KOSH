import { Card, CardContent } from "@/components/ui/card";

export function StatCard({ title, value, helper }: { title: string; value: string; helper?: string }) {
  return (
    <Card>
      <CardContent>
        <div className="text-sm text-slate-500">{title}</div>
        <div className="mt-2 text-2xl font-bold tracking-tight">{value}</div>
        {helper ? <div className="mt-1 text-xs text-slate-400">{helper}</div> : null}
      </CardContent>
    </Card>
  );
}
