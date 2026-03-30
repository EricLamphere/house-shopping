import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.models.house import House, ZillowData
from app.storage.house_store import HouseStore
from app.storage.assets_store import AssetsStore


@pytest.fixture()
def tmp_memory_dir(tmp_path: Path) -> Path:
    fixtures = Path(__file__).parent / "fixtures"
    assets_src = fixtures / "sample_assets.yml"
    if assets_src.exists():
        shutil.copy(assets_src, tmp_path / "assets.yml")
    return tmp_path


@pytest.fixture()
def house_store(tmp_memory_dir: Path) -> HouseStore:
    return HouseStore(tmp_memory_dir)


@pytest.fixture()
def assets_store(tmp_memory_dir: Path) -> AssetsStore:
    return AssetsStore(tmp_memory_dir)


@pytest.fixture()
def sample_house() -> House:
    now = datetime.now(timezone.utc)
    return House(
        id="test-house-001",
        zillow_url="https://www.zillow.com/homedetails/123-Main-St/12345_zpid/",
        zillow_data=ZillowData(
            address="123 Main St, Springfield, IL 62701",
            price=350000,
            beds=3,
            baths=2.5,
            sqft=2200,
            image_url="https://photos.zillowstatic.com/fp/test.jpg",
        ),
        is_favorite=False,
        added_at=now,
        updated_at=now,
    )


@pytest.fixture()
def sample_house_2() -> House:
    now = datetime.now(timezone.utc)
    return House(
        id="test-house-002",
        zillow_url="https://www.zillow.com/homedetails/456-Oak-Ave/67890_zpid/",
        zillow_data=ZillowData(
            address="456 Oak Ave, Springfield, IL 62702",
            price=425000,
            beds=4,
            baths=3.0,
            sqft=2800,
            image_url="https://photos.zillowstatic.com/fp/test2.jpg",
        ),
        is_favorite=False,
        added_at=now,
        updated_at=now,
    )


@pytest.fixture()
def app_client(tmp_memory_dir: Path):
    import os
    os.environ["MEMORY_DIR"] = str(tmp_memory_dir)
    # Re-import config to pick up new env var
    import app.config
    app.config.MEMORY_DIR = tmp_memory_dir
    app.config.HOUSES_FILE = tmp_memory_dir / "houses.json"
    app.config.ASSETS_FILE = tmp_memory_dir / "assets.yml"

    application = create_app()
    with TestClient(application) as client:
        yield client
