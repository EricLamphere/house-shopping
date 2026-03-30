from datetime import datetime, timezone

from app.models.house import House, ZillowData
from app.models.assets import UserAssets
from app.models.cost_estimate import CostEstimateInput, CostEstimateResult


class TestZillowData:
    def test_defaults(self):
        data = ZillowData()
        assert data.address == ""
        assert data.price is None
        assert data.beds is None
        assert data.baths is None
        assert data.sqft is None
        assert data.image_url is None

    def test_full_data(self):
        data = ZillowData(
            address="123 Main St",
            price=350000,
            beds=3,
            baths=2.5,
            sqft=2200,
            image_url="https://example.com/img.jpg",
        )
        assert data.price == 350000
        assert data.baths == 2.5

    def test_serialization_roundtrip(self):
        data = ZillowData(address="Test", price=100000)
        dumped = data.model_dump()
        restored = ZillowData.model_validate(dumped)
        assert restored == data


class TestHouse:
    def test_creation(self, sample_house):
        assert sample_house.id == "test-house-001"
        assert sample_house.zillow_data.price == 350000
        assert sample_house.is_favorite is False

    def test_serialization_roundtrip(self, sample_house):
        dumped = sample_house.model_dump(mode="json")
        restored = House.model_validate(dumped)
        assert restored.id == sample_house.id
        assert restored.zillow_data.address == sample_house.zillow_data.address

    def test_immutable_copy(self, sample_house):
        updated = sample_house.model_copy(update={"is_favorite": True})
        assert updated.is_favorite is True
        assert sample_house.is_favorite is False


class TestUserAssets:
    def test_defaults(self):
        assets = UserAssets()
        assert assets.annual_salary == 0.0
        assert assets.down_payment_percent == 20.0
        assert assets.loan_term_years == 30
        assert assets.interest_rate == 6.5

    def test_from_dict(self):
        assets = UserAssets.model_validate({
            "annual_salary": 100000,
            "savings": 50000,
        })
        assert assets.annual_salary == 100000
        assert assets.savings == 50000
        assert assets.interest_rate == 6.5  # default

    def test_serialization_roundtrip(self):
        assets = UserAssets(annual_salary=120000, savings=60000)
        dumped = assets.model_dump()
        restored = UserAssets.model_validate(dumped)
        assert restored == assets


class TestCostEstimateInput:
    def test_required_fields(self):
        inp = CostEstimateInput(
            purchase_price=400000,
            down_payment_percent=20.0,
            interest_rate=6.5,
            loan_term_years=30,
            annual_property_tax=5000,
            annual_insurance=1800,
        )
        assert inp.purchase_price == 400000
        assert inp.monthly_hoa == 0.0
        assert inp.monthly_heat == 0.0

    def test_optional_utilities(self):
        inp = CostEstimateInput(
            purchase_price=400000,
            down_payment_percent=20.0,
            interest_rate=6.5,
            loan_term_years=30,
            annual_property_tax=5000,
            annual_insurance=1800,
            monthly_heat=100,
            monthly_water=50,
            monthly_electric=120,
            monthly_internet=80,
        )
        assert inp.monthly_heat == 100
        assert inp.monthly_internet == 80


class TestCostEstimateResult:
    def test_creation(self):
        result = CostEstimateResult(
            principal_and_interest=2023.0,
            property_tax=417.0,
            insurance=150.0,
            pmi=0.0,
            hoa=0.0,
            utilities=350.0,
            total_monthly=2940.0,
            monthly_income=10000.0,
            monthly_existing_obligations=600.0,
            leftover_per_month=6460.0,
            down_payment=80000.0,
            closing_costs=12000.0,
            total_upfront=92000.0,
        )
        assert result.total_monthly == 2940.0
        assert result.leftover_per_month == 6460.0
