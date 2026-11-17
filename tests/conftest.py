from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"
SIMPLE_MSG = FIXTURES / "simple email with TO and CC_single.msg"
ATTACHMENTS_MSG = FIXTURES / "attachments.msg"


@pytest.fixture
def simple_msg() -> Path:
    return SIMPLE_MSG


@pytest.fixture
def attachments_msg() -> Path:
    return ATTACHMENTS_MSG
