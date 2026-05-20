export type User = {
  id: number;
  name: string;
  email: string;
  phone?: string | null;
  role: "admin" | "member" | string;
  
};

export type Member = User & {
  joined_at: string;
  is_active: boolean;
  total_paid: number;
};

export type Contribution = {
  id: number;
  member_id: number;
  member_name: string;
  month: string;
  amount: number;
  payment_method: string;
  status: "pending" | "approved" | "rejected" | string;
  photo_url?: string | null;
  remarks?: string | null;
  submitted_at: string;
  approved_at?: string | null;
  approved_by_name?: string | null;
  google_sheet_row_id?: string | null;
};

export type DashboardSummary = {
  total_saved: number;
  current_month_collected: number;
  current_month_expected: number;
  current_month_pending: number;
  pending_count: number;
  active_members: number;
  unpaid_members: string[];
  monthly_series: Array<{
    month: string;
    approved_amount: number;
    pending_amount: number;
  }>;
};
