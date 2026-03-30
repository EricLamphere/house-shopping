from app.models.cost_estimate import CostEstimateInput, CostEstimateResult


def calculate_monthly_mortgage(
    principal: float, annual_rate: float, term_years: int
) -> float:
    """Standard amortization: M = P * [r(1+r)^n] / [(1+r)^n - 1]."""
    if principal <= 0 or term_years <= 0:
        return 0.0
    if annual_rate <= 0:
        return principal / (term_years * 12)

    monthly_rate = annual_rate / 100 / 12
    num_payments = term_years * 12
    factor = (1 + monthly_rate) ** num_payments
    return principal * (monthly_rate * factor) / (factor - 1)


def calculate_pmi(loan_amount: float, home_value: float) -> float:
    """PMI at 0.75% annually when LTV > 80%."""
    if home_value <= 0:
        return 0.0
    ltv = loan_amount / home_value
    if ltv <= 0.80:
        return 0.0
    annual_pmi = loan_amount * 0.0075
    return annual_pmi / 12


def calculate_closing_costs(purchase_price: float, rate: float = 0.025) -> float:
    """Estimated closing costs as percentage of purchase price."""
    return purchase_price * rate


def calculate_full_estimate(inp: CostEstimateInput) -> CostEstimateResult:
    """Compute all cost components and return a complete result."""
    down_payment = inp.purchase_price * (inp.down_payment_percent / 100)
    loan_amount = inp.purchase_price - down_payment

    principal_and_interest = calculate_monthly_mortgage(
        loan_amount, inp.interest_rate, inp.loan_term_years
    )
    pmi = calculate_pmi(loan_amount, inp.purchase_price)
    property_tax = inp.annual_property_tax / 12
    insurance = inp.annual_insurance / 12
    utilities = (
        inp.monthly_heat + inp.monthly_water
        + inp.monthly_electric + inp.monthly_internet
    )
    closing_costs = calculate_closing_costs(inp.purchase_price)

    total_monthly = (
        principal_and_interest + property_tax + insurance
        + pmi + inp.monthly_hoa + utilities
    )

    monthly_income = inp.annual_salary / 12
    monthly_obligations = inp.monthly_loan_payments + inp.monthly_other_expenses
    leftover = monthly_income - total_monthly - monthly_obligations

    return CostEstimateResult(
        principal_and_interest=round(principal_and_interest, 2),
        property_tax=round(property_tax, 2),
        insurance=round(insurance, 2),
        pmi=round(pmi, 2),
        hoa=round(inp.monthly_hoa, 2),
        utilities=round(utilities, 2),
        total_monthly=round(total_monthly, 2),
        monthly_income=round(monthly_income, 2),
        monthly_existing_obligations=round(monthly_obligations, 2),
        leftover_per_month=round(leftover, 2),
        down_payment=round(down_payment, 2),
        closing_costs=round(closing_costs, 2),
        total_upfront=round(down_payment + closing_costs, 2),
    )
