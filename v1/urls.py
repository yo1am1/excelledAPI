from django.urls import path

from . import views

urlpatterns = [
    path("v1/", views.UrlsList.as_view(), name="urls-list"),
    path("v1/sheets/", views.SheetList.as_view(), name="sheet-list"),
    path("v1/cells/", views.CellList.as_view(), name="cell-list"),
    path("v1/<sheet_id>/<cell_id>/", views.CellDetail.as_view(), name="cell-detail"),
    path("v1/<sheet_id>/", views.SheetDetail.as_view(), name="sheet-detail"),
]
