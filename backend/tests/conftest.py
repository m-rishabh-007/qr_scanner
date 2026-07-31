import pytest
from django.core.management import call_command


@pytest.fixture
def seeded_catalog(db):
    call_command("seed_initial_catalog", verbosity=0)
