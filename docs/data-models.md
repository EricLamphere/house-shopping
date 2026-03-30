# Data Models

All models are defined with Pydantic v2 in `app/models/`. Validation happens at system boundaries — when reading from storage and when receiving form input.

## House

Defined in `app/models/house.py`. The root entity for a saved listing.

```python
class House(BaseModel):
    id: str                              # UUID, generated on creation
    zillow_url: str                      # Source URL (optional, for reference)
    zillow_data: ZillowData              # Listing details (nested)
    notes: str                           # Free-text user notes
    annual_property_tax: Optional[int]   # Annual property tax in dollars
    annual_insurance: Optional[int]      # Annual homeowner's insurance
    monthly_pmi_override: Optional[int]  # Quoted PMI; bypasses auto-calculation
    monthly_heat: Optional[int]
    monthly_water: Optional[int]
    monthly_electric: Optional[int]
    monthly_internet: Optional[int]
    is_favorite: bool                    # Starred by user
    favorite_sort_order: Optional[int]   # Position in favorites grid
    added_at: datetime                   # UTC
    updated_at: datetime                 # UTC
```

### ZillowData

Nested inside `House`. Contains the listing-specific details sourced from the listing page (or entered manually).

```python
class ZillowData(BaseModel):
    address: str = ""
    price: Optional[int] = None
    beds: Optional[int] = None
    baths: Optional[float] = None
    sqft: Optional[int] = None
    image_url: Optional[str] = None
```

## Link

Defined in `app/models/link.py`. Represents a saved reference link.

```python
class Link(BaseModel):
    id: str           # UUID, generated on creation
    text: str         # Display text shown in the UI
    url: str          # Full URL (validated as a URL by the browser input)
    sort_order: int   # Zero-based position; controls display order
```

New links are appended with `sort_order = max(existing) + 1`. Drag-and-drop reorder updates all `sort_order` values by sending the full ordered ID list to `PUT /links/order`.

## UserAssets

Defined in `app/models/assets.py`. The user's financial profile, used to pre-fill cost estimator fields.

```python
class UserAssets(BaseModel):
    annual_salary: float = 0.0
    monthly_take_home: Optional[float] = None   # Overrides salary/12 for budget math
    savings: float = 0.0
    retirement_balance: float = 0.0
    monthly_loan_payments: float = 0.0          # Car loans, student debt, etc.
    monthly_other_expenses: float = 0.0         # Subscriptions, recurring costs
    credit_score: Optional[int] = None
    down_payment_percent: float = 20.0
    loan_term_years: int = 30
    interest_rate: float = 6.5                  # Annual percentage rate
```

`monthly_take_home` takes precedence over `annual_salary / 12` when calculating leftover budget. Set this to your actual post-tax, post-deduction take-home pay for accurate results.

## CostEstimateInput

Defined in `app/models/cost_estimate.py`. Represents the submitted cost estimator form.

```python
class CostEstimateInput(BaseModel):
    house_id: Optional[str] = None
    purchase_price: int
    down_payment_percent: float
    interest_rate: float
    loan_term_years: int
    annual_property_tax: float
    annual_insurance: float
    monthly_pmi_override: Optional[float] = None  # Blank = auto-calculate
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
```

## CostEstimateResult

Output from `calculate_full_estimate()`. All amounts are in dollars per month unless noted.

```python
class CostEstimateResult(BaseModel):
    principal_and_interest: float    # Monthly mortgage payment
    property_tax: float              # annual_property_tax / 12
    insurance: float                 # annual_insurance / 12
    pmi: float                       # Monthly PMI (override or calculated)
    hoa: float                       # Monthly HOA
    utilities: float                 # Sum of heat + water + electric + internet
    total_monthly: float             # Sum of all above
    monthly_income: float            # take_home or salary/12
    monthly_existing_obligations: float
    leftover_per_month: float        # income - total_monthly - obligations
    down_payment: float              # Upfront, dollars
    closing_costs: float             # Estimated upfront, dollars
    total_upfront: float             # down_payment + closing_costs
```

## Storage Format

Houses are stored as a JSON array in `memory/houses.json`. Each element is the result of `house.model_dump(mode="json")`, which serializes datetimes as ISO 8601 strings.

Links are stored as a JSON array in `memory/links.json`. Each element is a plain `Link` dict — no datetime fields. Example:

```json
[
  {"id": "a1b2c3...", "text": "Mortgage Calculator", "url": "https://example.com", "sort_order": 0},
  {"id": "d4e5f6...", "text": "School District Ratings", "url": "https://example.com", "sort_order": 1}
]
```

UserAssets is stored as a YAML document in `memory/assets.yml`. See `memory/README.md` for the full template.
