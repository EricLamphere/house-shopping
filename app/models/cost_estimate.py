from pydantic import BaseModel
from typing import Literal, Optional


class CostEstimateInput(BaseModel):
    house_id: Optional[str] = None
    purchase_price: int
    down_payment_percent: Optional[float] = None
    down_payment_dollars: Optional[float] = None
    down_payment_mode: Literal["percent", "dollars"] = "percent"
    interest_rate: float
    loan_term_years: int
    annual_property_tax: float
    annual_insurance: float
    monthly_pmi_override: Optional[float] = None
    monthly_hoa: float = 0.0
    monthly_heat: float = 0.0
    monthly_water: float = 0.0
    monthly_electric: float = 0.0
    monthly_internet: float = 0.0
    annual_salary: float = 0.0
    monthly_take_home: Optional[float] = None
    monthly_loan_payments: float = 0.0
    monthly_other_expenses: float = 0.0
    savings: float = 0.0


class CostEstimateResult(BaseModel):
    principal_and_interest: float
    property_tax: float
    insurance: float
    pmi: float
    hoa: float
    utilities: float
    total_monthly: float
    total_monthly_without_utilities: float
    monthly_income: float
    monthly_existing_obligations: float
    disposable_income: float
    leftover_per_month: float
    down_payment: float
    closing_costs: float
    total_upfront: float
    pct_of_disposable_income: Optional[float]
    pct_of_disposable_income_with_utilities: Optional[float]
    pct_of_salary: Optional[float]
    pct_of_salary_with_utilities: Optional[float]
