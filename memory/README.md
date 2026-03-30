# memory/

Runtime data directory, mounted as a Docker volume. Contents are gitignored (except this file).

## Files

| File | Description |
|------|-------------|
| `houses.json` | Saved house listings. Auto-created on first use. |
| `links.json` | Saved links (resources, lenders, etc). Auto-created on first use. |
| `assets.yml` | Your financial profile for cost estimates. Create this manually — see template below. |

## assets.yml

Create `memory/assets.yml` with your financial details:

```yaml
# Income & savings
annual_salary: 0
monthly_take_home: 0        # actual take-home after taxes/deductions; overrides annual_salary for budget calculations
savings: 0
retirement_balance: 0

# Monthly obligations
monthly_loan_payments: 0    # car loans, student debt, etc.
monthly_other_expenses: 0   # subscriptions, recurring costs, etc.

# Credit & loan preferences
credit_score: 0
down_payment_percent: 10.0  # percentage, e.g. 10.0 for 10%
loan_term_years: 30
interest_rate: 6.5          # annual percentage rate
```

All fields default to `0` if the file is missing or a field is omitted.
