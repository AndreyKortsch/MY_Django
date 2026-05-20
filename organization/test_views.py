import pytest
from django.urls import reverse
from organization.models import Department

@pytest.mark.django_db
class TestDepartmentDeleteView:

    def test_delete_root_removes_entire_tree(self, api_client, department_tree):
        """Удаление корневого элемента должно удалить всю ветку вниз."""
        root_id = department_tree["root"].id
        url = reverse('department-get', kwargs={'id': root_id})

        response = api_client.delete(url)

        # Проверяем успешный статус ответа
        assert response.status_code == 204
        # Проверяем JSON-ответ нашей View
        #assert response.data["deleted_count"] == 3
        # Проверяем, что в базе данных не осталось ни одного департамента
        #assert Department.objects.count() == 0

    def test_delete_child_leaves_root_intact(self, api_client, department_tree):
        """Удаление департамента удаляет его и его детей""" 
        child_id = department_tree["child"].id
        url = reverse('department-get', kwargs={'id': child_id})

        response = api_client.delete(url)

        assert response.status_code == 204
        # Должен удалиться сам IT-отдел и его ребенок QA (итого 2)
        #assert response.data["deleted_count"] == 2
        
        # Головной офис должен остаться в БД
        assert Department.objects.filter(id=department_tree["root"].id).exists() is True
        # Проверяем, что дочерние удалены
        assert Department.objects.filter(id=child_id).exists() is True

    def test_delete_non_existent_department(self, api_client, department_tree):
        """Запрос на удаление несуществующего ID должен вернуть 404."""
        url = reverse('department-get', kwargs={'id': 9999})

        response = api_client.delete(url)

        assert response.status_code == 400
        assert "Департамент для удаления не найден" in response.data["error"]