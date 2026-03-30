# Cost Calculator

The cost calculator lives in `app/services/cost_calculator.py`. It consists of pure functions — no I/O, no side effects.

## Mortgage Payment

Standard amortization formula:

```
M = P * [r(1+r)^n] / [(1+r)^n - 1]

Where:
  P = principal (purchase price - down payment)
  r = monthly interest rate (annual rate / 12 / 100)
  n = total number of payments (loan_term_years * 12)
```

If `annual_rate` is 0, the payment is `principal / n` (interest-free amortization).

## PMI

PMI is charged when the loan-to-value ratio exceeds 80% — i.e. when the down payment is less than 20%.

```
LTV = loan_amount / purchase_price

If LTV > 0.80:
    annual_pmi = loan_amount * 0.0075  (0.75% annually)
    monthly_pmi = annual_pmi / 12
Else:
    monthly_pmi = 0
```

### PMI Override

The calculated PMI tends to overestimate for lower loan amounts. If you've been quoted a specific PMI amount by your lender, enter it in the **Monthly PMI** field in the house edit modal. This value bypasses the formula entirely and is passed through directly to the result.

Example: A quoted PMI of $90/month should be entered as `90`.

## Closing Costs

Estimated at **2.5% of the purchase price**. This is a rough estimate — actual closing costs vary by state, lender, and loan type.

## Income and Leftover Budget

```
monthly_income = monthly_take_home  (if set)
               OR  annual_salary / 12  (fallback)

leftover = monthly_income - total_monthly - monthly_obligations

Where:
  total_monthly       = P&I + tax + insurance + PMI + HOA + utilities
  monthly_obligations = monthly_loan_payments + monthly_other_expenses
```

`monthly_take_home` in `assets.yml` is the recommended value to set — it's your actual post-tax, post-401k take-home, which is what you actually have to spend. `annual_salary` divided by 12 will always overestimate available income.

## Full Estimate Output

| Field | Calculation |
|-------|-------------|
| Principal & Interest | Amortization formula |
| Property Tax | `annual_property_tax / 12` |
| Insurance | `annual_insurance / 12` |
| PMI | Override or `loan_amount * 0.0075 / 12` |
| HOA | Passed through from input |
| Utilities | `heat + water + electric + internet` |
| **Total Monthly** | Sum of all above |
| Down Payment | `purchase_price * down_payment_percent / 100` |
| Closing Costs | `purchase_price * 0.025` |
| **Total Upfront** | Down payment + closing costs |
| Monthly Take-Home | From `monthly_take_home` or `annual_salary / 12` |
| Leftover | Take-home − total monthly − obligations |
