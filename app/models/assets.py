from pydantic import BaseModel
from typing import Optional


class UserAssets(BaseModel):
    annual_salary: float = 0.0
    monthly_take_home: Optional[float] = None
    savings: float = 0.0
    retirement_balance: float = 0.0
    monthly_loan_payments: float = 0.0
    monthly_other_expenses: float = 0.0
    credit_score: Optional[int] = None
    down_payment_percent: float = 20.0
    loan_term_years: int = 30
    interest_rate: float = 6.5
