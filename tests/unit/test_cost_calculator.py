import pytest

from app.services.cost_calculator import (
    calculate_monthly_mortgage,
    calculate_pmi,
    calculate_closing_costs,
    calculate_full_estimate,
)
from app.models.cost_estimate import CostEstimateInput


class TestMonthlyMortgage:
    def test_standard_30yr(self):
        # $320,000 loan at 6.5% for 30 years
        # Expected ~$2,023/month
        payment = calculate_monthly_mortgage(320000, 6.5, 30)
        assert 2020 < payment < 2030

    def test_15yr_loan(self):
        payment = calculate_monthly_mortgage(320000, 6.5, 15)
        # 15yr should be higher than 30yr
        payment_30 = calculate_monthly_mortgage(320000, 6.5, 30)
        assert payment > payment_30

    def test_zero_principal(self):
        assert calculate_monthly_mortgage(0, 6.5, 30) == 0.0

    def test_zero_rate(self):
        # 0% interest = simple division
        payment = calculate_monthly_mortgage(360000, 0, 30)
        assert payment == 1000.0

    def test_zero_term(self):
        assert calculate_monthly_mortgage(320000, 6.5, 0) == 0.0


class TestPMI:
    def test_pmi_applied_below_20_percent_down(self):
        # 10% down on $400,000 = $360,000 loan = LTV 90%
        pmi = calculate_pmi(360000, 400000)
        assert pmi > 0
        # 0.75% of $360,000 / 12 = $225
        assert abs(pmi - 225) < 1

    def test_no_pmi_at_20_percent_down(self):
        # 20% down on $400,000 = $320,000 loan = LTV 80%
        pmi = calculate_pmi(320000, 400000)
        assert pmi == 0.0

    def test_no_pmi_above_20_percent_down(self):
        # 30% down
        pmi = calculate_pmi(280000, 400000)
        assert pmi == 0.0

    def test_zero_home_value(self):
        assert calculate_pmi(100000, 0) == 0.0


class TestClosingCosts:
    def test_default_rate(self):
        # 3% of $400,000
        assert calculate_closing_costs(400000) == 12000

    def test_custom_rate(self):
        assert calculate_closing_costs(400000, 0.05) == 20000


class TestFullEstimate:
    @pytest.fixture()
    def standard_input(self) -> CostEstimateInput:
        return CostEstimateInput(
            purchase_price=400000,
            down_payment_percent=20.0,
            interest_rate=6.5,
            loan_term_years=30,
            annual_property_tax=6000,
            annual_insurance=2400,
            monthly_hoa=100,
            monthly_heat=150,
            monthly_water=60,
            monthly_electric=120,
            monthly_internet=80,
            annual_salary=120000,
            monthly_loan_payments=400,
            monthly_other_expenses=200,
            savings=60000,
        )

    def test_down_payment(self, standard_input):
        result = calculate_full_estimate(standard_input)
        assert result.down_payment == 80000

    def test_no_pmi_at_20_percent(self, standard_input):
        result = calculate_full_estimate(standard_input)
        assert result.pmi == 0.0

    def test_pmi_with_low_down_payment(self, standard_input):
        inp = standard_input.model_copy(update={"down_payment_percent": 10.0})
        result = calculate_full_estimate(inp)
        assert result.pmi > 0

    def test_utilities_sum(self, standard_input):
        result = calculate_full_estimate(standard_input)
        expected = 150 + 60 + 120 + 80  # heat + water + electric + internet
        assert result.utilities == expected

    def test_total_monthly_includes_all(self, standard_input):
        result = calculate_full_estimate(standard_input)
        expected = (
            result.principal_and_interest
            + result.property_tax
            + result.insurance
            + result.pmi
            + result.hoa
            + result.utilities
        )
        assert abs(result.total_monthly - expected) < 0.01

    def test_leftover_calculation(self, standard_input):
        result = calculate_full_estimate(standard_input)
        expected = result.monthly_income - result.total_monthly - result.monthly_existing_obligations
        assert abs(result.leftover_per_month - expected) < 0.01

    def test_closing_costs(self, standard_input):
        result = calculate_full_estimate(standard_input)
        assert result.closing_costs == 12000  # 3% of 400k

    def test_total_upfront(self, standard_input):
        result = calculate_full_estimate(standard_input)
        assert result.total_upfront == result.down_payment + result.closing_costs

    def test_monthly_income(self, standard_input):
        result = calculate_full_estimate(standard_input)
        assert result.monthly_income == 10000  # 120k / 12

    def test_100_percent_down(self):
        inp = CostEstimateInput(
            purchase_price=400000,
            down_payment_percent=100.0,
            interest_rate=6.5,
            loan_term_years=30,
            annual_property_tax=6000,
            annual_insurance=2400,
        )
        result = calculate_full_estimate(inp)
        assert result.principal_and_interest == 0.0
        assert result.pmi == 0.0
        assert result.down_payment == 400000
