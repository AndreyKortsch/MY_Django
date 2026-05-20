import pytest
from .models import Department
from rest_framework.test import APIClient
from django.db import transaction

@pytest.fixture
def api_client():
    """Фикстура тестового клиента DRF."""
    return APIClient()

@pytest.fixture
def department_tree(db):
    """Создает иерархию департаментов: Головной (1) -> IT (2) -> QA (3)."""
    with transaction.atomic():
        root = Department.objects.create(name="Головной офис", parent=None)
        child = Department.objects.create(name="IT Департамент", parent=root)
        grandchild = Department.objects.create(name="Отдел QA", parent=child)
    
        yield {
            "root": root,
            "child": child,
            "grandchild": grandchild
        }
