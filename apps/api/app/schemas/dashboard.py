from pydantic import BaseModel


class MonthlyPoint(BaseModel):
    month: str
    approved_amount: int
    pending_amount: int


class DashboardSummary(BaseModel):
    total_saved: int
    current_month_collected: int
    current_month_expected: int
    current_month_pending: int
    pending_count: int
    active_members: int
    unpaid_members: list[str]
    monthly_series: list[MonthlyPoint]
