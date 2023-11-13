import re

from django.http import Http404
from rest_framework import generics, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from .models import Sheet, Cell
from .serializers import (
    CellSerializer,
    SheetCreateSerializer,
    CellDetailSerializer,
    CellResponseSerializer,
)


class UrlsList(APIView):
    description = "List of all available urls"

    def get(self, request):
        urls = {
            "List of all available urls": reverse("urls-list", request=request),
            "List all sheets and create new": reverse("sheet-list", request=request),
            "Sheet detail and delete": reverse(
                "sheet-detail", request=request, args=["sheet_id"]
            ),
            "Cell detail": reverse(
                "cell-detail", request=request, args=["sheet_id", "cell_id"]
            ),
        }
        return Response(urls, status=200)


class CellDetail(APIView):
    description = "Cell detail"

    def get(self, request, sheet_id, cell_id):
        try:
            sheet = Sheet.objects.get(sheet_id=sheet_id)
            cell = Cell.objects.get(sheet=sheet, cell_id=cell_id)
        except (Sheet.DoesNotExist, Cell.DoesNotExist):
            raise Http404
        serializer = CellResponseSerializer(cell)
        return Response(serializer.data, status=200)

    def post(self, request, cell_id, sheet_id):
        try:
            sheet = Sheet.objects.get(sheet_id=sheet_id)
            cell = Cell.objects.get(cell_id=cell_id, sheet=sheet)
        except Cell.DoesNotExist:
            raise Http404

        cell.value = request.data.get("value")
        value = request.data.get("value")

        if value.startswith("="):
            formula = value[1:]

            variable_names = re.findall(r"[a-zA-Z_][a-zA-Z0-9_]*", formula)

            variables = {}

            for var_name in variable_names:
                try:
                    var_cell = Cell.objects.get(cell_id=var_name, sheet=sheet)
                    if var_cell.result is not None and var_cell.result != "":
                        variables[var_name] = float(var_cell.result)
                    else:
                        variables[var_name] = 0.0
                except Cell.DoesNotExist:
                    raise Http404

            try:
                for var_name, var_value in variables.items():
                    formula = formula.replace(var_name, str(var_value))

                result = eval(formula)

                cell.result = str(result)

                cell.save()

                serializer = CellResponseSerializer(cell)
                return Response(serializer.data, status=200)

            except Exception as e:
                return Response({"error": str(e)}, status=400)
        else:
            cell.result = cell.value
            cell.save()
            serializer = CellResponseSerializer(cell)
            return Response(serializer.data, status=200)

    def delete(self, request, sheet_id, cell_id):
        try:
            sheet = Sheet.objects.get(sheet_id=sheet_id)
            cell = Cell.objects.get(cell_id=cell_id, sheet=sheet)
        except Cell.DoesNotExist:
            raise Http404
        cell.delete()
        return Response({"Successfully deleted"}, status=204)


class SheetList(generics.ListCreateAPIView):
    description = "List all sheets and create new"

    queryset = Sheet.objects.all()
    serializer_class = SheetCreateSerializer


class CellList(APIView):
    description = "List all cells and create new"

    queryset = Cell.objects.all()
    serializer_class = CellDetailSerializer

    def get(self, request, *args, **kwargs):
        cells = Cell.objects.all()
        serializer = CellSerializer(cells, many=True)
        return Response(serializer.data, status=200)

    def post(self, request, *args, **kwargs):
        serializer = CellDetailSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            sheet_id = request.data.get("sheet")

            try:
                sheet = Sheet.objects.get(id=sheet_id)
            except Sheet.DoesNotExist:
                return Response({"error": "Sheet not found"}, status=404)

            sheet.cells.add(serializer.instance)
            sheet.save()

            return Response({"Successfully created"}, status=201)
        return Response(serializer.errors, status=400)


class SheetDetail(APIView):
    description = "Sheet detail and delete"

    def get(self, request, sheet_id):
        sheet = get_object_or_404(Sheet, sheet_id__iexact=sheet_id)

        cell_data = {}

        cells = Cell.objects.filter(sheet=sheet)
        for cell in cells:
            cell_data[cell.cell_id] = {"value": cell.value, "result": cell.result}

        return Response(cell_data, status=status.HTTP_200_OK)

    def delete(self, request, sheet_id):
        try:
            sheet = Sheet.objects.get(sheet_id=sheet_id)
        except Sheet.DoesNotExist:
            raise Http404
        sheet.delete()
        return Response({"Successfully deleted"}, status=204)
