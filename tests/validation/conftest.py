"""Auto-score before quality scorer tests."""

import pytest


@pytest.fixture(autouse=True, scope="session")
def auto_score_db():
    """Run batch scorer before any quality tests."""
    from src.common.quality.batch_quality_scorer import batch_score_all
    batch_score_all(dry_run=False)
    yield
