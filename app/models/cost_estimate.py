from pydantic import BaseModel
from typing import Optional


class CostEstimateInput(BaseModel):
    house_id: Optional[str] = None
    purchase_price: int
    down_payment_percent: float
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
    monthly_income: float
    monthly_existing_obligations: float
    leftover_per_month: float
    down_payment: float
    closing_costs: float
    total_upfront: float
