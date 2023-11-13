import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .models import Sheet, Cell


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def sheet():
    return Sheet.objects.create(sheet_id="test_sheet")


@pytest.mark.django_db
def test_create_cell_with_value(api_client, sheet):
    cell_data = {"cell_id": "var0", "value": "10", "sheet": sheet.id}
    response = api_client.post(reverse("cell-list"), cell_data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert Cell.objects.count() == 1
    assert Cell.objects.get().result == "10"


@pytest.mark.django_db
def test_create_cell_with_formula(api_client, sheet):
    Cell.objects.create(cell_id="var0", value="10", sheet=sheet, result="10")
    cell_data = {"cell_id": "var1", "value": "=var0+5", "sheet": sheet.id}
    response = api_client.post(reverse("cell-list"), cell_data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert Cell.objects.count() == 2
    assert Cell.objects.get(cell_id="var1").result == "15.0"


@pytest.mark.django_db
def test_create_cell_with_invalid_formula(api_client, sheet):
    cell_data = {
        "cell_id": "var2",
        "value": "=var0+",
        "sheet": sheet.id,
    }
    response = api_client.post(reverse("cell-list"), cell_data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert Cell.objects.count() == 0


@pytest.mark.django_db
def test_list_cells(api_client, sheet):
    Cell.objects.create(cell_id="var0", value="10", sheet=sheet, result="10")
    Cell.objects.create(cell_id="var1", value="20", sheet=sheet, result="20")
    response = api_client.get(reverse("cell-list"))
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2


@pytest.mark.django_db
def test_delete_cell(api_client, sheet):
    cell = Cell.objects.create(cell_id="var0", value="10", sheet=sheet, result="10")
    response = api_client.delete(
        reverse("cell-detail", args=[sheet.sheet_id, cell.cell_id]),
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Cell.objects.filter(id=cell.id).exists()


@pytest.mark.django_db
def test_create_invalid_cell(api_client, sheet):
    invalid_cell_data = {"value": "10"}
    response = api_client.post(reverse("cell-list"), invalid_cell_data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_update_cell_with_formula(api_client, sheet):
    cell = Cell.objects.create(cell_id="var0", value="10", sheet=sheet, result="10")
    cell_data = {"value": "=var0+5"}
    response = api_client.post(
        reverse("cell-detail", args=[sheet.sheet_id, cell.cell_id]),
        cell_data,
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    updated_cell = Cell.objects.get(id=cell.id)
    assert updated_cell.result == "15.0"


@pytest.mark.django_db
def test_create_duplicate_cell(api_client, sheet):
    cell_data = {"cell_id": "var0", "value": "10", "sheet": sheet.id}
    response1 = api_client.post(reverse("cell-list"), cell_data, format="json")
    assert response1.status_code == status.HTTP_201_CREATED

    response2 = api_client.post(reverse("cell-list"), cell_data, format="json")
    assert response2.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_retrieve_non_existent_cell(api_client, sheet):
    non_existent_cell_id = "non_existent_cell"
    response = api_client.get(
        reverse("cell-detail", args=[sheet.sheet_id, non_existent_cell_id])
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_update_non_existent_cell(api_client, sheet):
    non_existent_cell_id = "non_existent_cell"
    cell_data = {"value": "10"}
    response = api_client.post(
        reverse("cell-detail", args=[sheet.sheet_id, non_existent_cell_id]),
        cell_data,
        format="json",
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_delete_non_existent_cell(api_client, sheet):
    non_existent_cell_id = "non_existent_cell"
    response = api_client.delete(
        reverse("cell-detail", args=[sheet.sheet_id, non_existent_cell_id])
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_list_sheets(api_client, sheet):
    response = api_client.get(reverse("sheet-list"))
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1


@pytest.mark.django_db
def test_delete_sheet(api_client, sheet):
    response = api_client.delete(reverse("sheet-detail", args=[sheet.sheet_id]))
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Sheet.objects.filter(id=sheet.id).exists()
