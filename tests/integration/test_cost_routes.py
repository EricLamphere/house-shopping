class TestCostEstimatorPage:
    def test_get_page(self, app_client):
        response = app_client.get("/cost-estimator")
        assert response.status_code == 200
        assert "Cost Estimator" in response.text

    def test_get_page_for_nonexistent_house(self, app_client):
        response = app_client.get("/cost-estimator/nonexistent")
        assert response.status_code == 200


class TestCalculate:
    def test_basic_calculation(self, app_client):
        response = app_client.post("/cost-estimator/calculate", data={
            "purchase_price": 400000,
            "down_payment_percent": 20.0,
            "interest_rate": 6.5,
            "loan_term_years": 30,
            "annual_property_tax": 6000,
            "annual_insurance": 2400,
            "monthly_hoa": 0,
            "monthly_heat": 150,
            "monthly_water": 60,
            "monthly_electric": 120,
            "monthly_internet": 80,
            "annual_salary": 120000,
            "monthly_loan_payments": 400,
            "monthly_other_expenses": 200,
            "savings": 60000,
        })
        assert response.status_code == 200
        assert "Total Monthly Payment" in response.text
        assert "Leftover" in response.text

    def test_calculation_with_pmi(self, app_client):
        response = app_client.post("/cost-estimator/calculate", data={
            "purchase_price": 400000,
            "down_payment_percent": 10.0,
            "interest_rate": 6.5,
            "loan_term_years": 30,
            "annual_property_tax": 6000,
            "annual_insurance": 2400,
        })
        assert response.status_code == 200
        assert "PMI" in response.text


class TestAssetsRoutes:
    def test_get_assets(self, app_client):
        response = app_client.get("/assets")
        assert response.status_code == 200
        data = response.json()
        assert "annual_salary" in data

    def test_update_assets(self, app_client):
        response = app_client.put("/assets", json={
            "annual_salary": 150000,
            "savings": 80000,
            "retirement_balance": 100000,
            "monthly_loan_payments": 300,
            "monthly_other_expenses": 100,
            "down_payment_percent": 25.0,
            "loan_term_years": 30,
            "interest_rate": 6.0,
        })
        assert response.status_code == 200
        data = response.json()
        assert data["annual_salary"] == 150000

        # Verify persistence
        response2 = app_client.get("/assets")
        assert response2.json()["annual_salary"] == 150000
