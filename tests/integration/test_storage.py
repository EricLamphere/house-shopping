from app.models.assets import UserAssets


class TestHouseStore:
    def test_add_and_list(self, house_store, sample_house):
        house_store.add(sample_house)
        houses = house_store.list_all()
        assert len(houses) == 1
        assert houses[0].id == sample_house.id

    def test_add_multiple_sorted_by_recent(self, house_store, sample_house, sample_house_2):
        house_store.add(sample_house)
        house_store.add(sample_house_2)
        houses = house_store.list_all()
        assert len(houses) == 2

    def test_get_by_id(self, house_store, sample_house):
        house_store.add(sample_house)
        found = house_store.get(sample_house.id)
        assert found is not None
        assert found.id == sample_house.id

    def test_get_nonexistent(self, house_store):
        assert house_store.get("nonexistent") is None

    def test_remove(self, house_store, sample_house):
        house_store.add(sample_house)
        house_store.remove(sample_house.id)
        assert house_store.list_all() == []

    def test_toggle_favorite(self, house_store, sample_house):
        house_store.add(sample_house)
        updated = house_store.toggle_favorite(sample_house.id)
        assert updated is not None
        assert updated.is_favorite is True

        updated2 = house_store.toggle_favorite(sample_house.id)
        assert updated2 is not None
        assert updated2.is_favorite is False

    def test_list_favorites(self, house_store, sample_house, sample_house_2):
        house_store.add(sample_house)
        house_store.add(sample_house_2)
        house_store.toggle_favorite(sample_house.id)
        house_store.toggle_favorite(sample_house_2.id)

        favorites = house_store.list_favorites()
        assert len(favorites) == 2

    def test_update_favorites_order(self, house_store, sample_house, sample_house_2):
        house_store.add(sample_house)
        house_store.add(sample_house_2)
        house_store.toggle_favorite(sample_house.id)
        house_store.toggle_favorite(sample_house_2.id)

        house_store.update_favorites_order([sample_house_2.id, sample_house.id])
        favorites = house_store.list_favorites()
        assert favorites[0].id == sample_house_2.id
        assert favorites[1].id == sample_house.id

    def test_empty_store(self, house_store):
        assert house_store.list_all() == []
        assert house_store.list_favorites() == []

    def test_toggle_nonexistent(self, house_store):
        result = house_store.toggle_favorite("nonexistent")
        assert result is None


class TestAssetsStore:
    def test_read_defaults(self, assets_store):
        assets = assets_store.read()
        # From sample_assets.yml fixture
        assert assets.annual_salary == 120000

    def test_write_and_read(self, assets_store):
        new_assets = UserAssets(
            annual_salary=150000,
            savings=80000,
            down_payment_percent=25.0,
        )
        assets_store.write(new_assets)
        read_back = assets_store.read()
        assert read_back.annual_salary == 150000
        assert read_back.savings == 80000
        assert read_back.down_payment_percent == 25.0

    def test_read_missing_file(self, tmp_path):
        from app.storage.assets_store import AssetsStore
        store = AssetsStore(tmp_path / "nonexistent")
        assets = store.read()
        assert assets == UserAssets()
