from pathlib import Path

import pytest

from sitedrainguard.config import BASE_MODEL_PATH, COSTS_PATH, MODEL_METADATA_PATH
from sitedrainguard.services.analysis_service import AnalysisService


@pytest.fixture(scope="session")
def project_root() -> Path:
    return BASE_MODEL_PATH.parents[2]


@pytest.fixture(scope="session")
def service() -> AnalysisService:
    return AnalysisService(BASE_MODEL_PATH, MODEL_METADATA_PATH, COSTS_PATH)
