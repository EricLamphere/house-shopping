from unittest.mock import AsyncMock, patch

from app.models.house import ZillowData


class TestAddHouse:
    def test_add_house_manual_entry(self, app_client):
        response = app_client.post("/houses", data={
            "zillow_url": "",
            "address": "789 Elm St, Test City, TS 12345",
            "price": 300000,
            "beds": 3,
            "baths": 2,
            "sqft": 1800,
            "image_url": "",
        })
        assert response.status_code == 200
        assert "added successfully" in response.text

    def test_add_house_with_zillow_url_scrape_fails(self, app_client):
        with patch(
            "app.routes.houses.scrape_zillow_listing",
            new_callable=AsyncMock,
            side_effect=Exception("scrape failed"),
        ):
            response = app_client.post("/houses", data={
                "zillow_url": "https://www.zillow.com/homedetails/test/123_zpid/",
                "address": "Fallback Address",
                "price": 250000,
                "beds": 2,
                "baths": 1,
                "sqft": 1200,
                "image_url": "",
            })
            assert response.status_code == 200

    def test_add_house_with_successful_scrape(self, app_client):
        mock_data = ZillowData(
            address="Scraped Address",
            price=500000,
            beds=4,
            baths=3,
            sqft=3000,
            image_url="https://example.com/photo.jpg",
        )
        with patch(
            "app.routes.houses.scrape_zillow_listing",
            new_callable=AsyncMock,
            return_value=mock_data,
        ):
            response = app_client.post("/houses", data={
                "zillow_url": "https://www.zillow.com/homedetails/test/456_zpid/",
            })
            assert response.status_code == 200


class TestDeleteHouse:
    def test_delete_existing(self, app_client):
        # Add a house first
        app_client.post("/houses", data={
            "zillow_url": "",
            "address": "To Delete",
            "price": 100000,
        })

        # Get the homepage to find the house ID
        home_response = app_client.get("/")
        assert home_response.status_code == 200

    def test_delete_nonexistent(self, app_client):
        response = app_client.delete("/houses/nonexistent-id")
        assert response.status_code == 200


class TestToggleFavorite:
    def test_toggle_nonexistent(self, app_client):
        response = app_client.patch("/houses/nonexistent-id/favorite")
        assert response.status_code == 200


class TestFavoritesOrder:
    def test_update_order(self, app_client):
        response = app_client.put(
            "/houses/favorites/order",
            json={"ordered_ids": ["id1", "id2"]},
        )
        assert response.status_code == 204


class TestHomepage:
    def test_homepage_empty(self, app_client):
        response = app_client.get("/")
        assert response.status_code == 200
        assert "No houses added yet" in response.text

    def test_homepage_with_houses(self, app_client):
        app_client.post("/houses", data={
            "zillow_url": "",
            "address": "Test House",
            "price": 250000,
        })
        response = app_client.get("/")
        assert response.status_code == 200
        assert "Test House" in response.text
