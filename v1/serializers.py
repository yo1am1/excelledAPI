import re

from rest_framework import serializers

from .models import Sheet, Cell


class CellSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cell
        fields = "__all__"


class CellResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cell
        fields = ["value", "result"]


class CellSheetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cell
        fields = ["cell_id", "value", "result"]


class CellDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cell
        fields = ["cell_id", "value", "sheet"]

    def validate_cell_id(self, value):
        # Check if the cell_id starts with a number
        if re.match(r"^[0-9]", value):
            raise serializers.ValidationError("Cell names cannot start with a number.")
        return value

    def create(self, validated_data):
        value = validated_data.get("value")

        if value.startswith("="):
            formula = value[1:]

            variable_names = re.findall(r"[a-zA-Z_][a-zA-Z0-9_]*", formula)

            variables = {}

            for var_name in variable_names:
                try:
                    var_cell = Cell.objects.get(
                        cell_id=var_name, sheet=validated_data["sheet"]
                    )
                    if var_cell.result is not None and var_cell.result != "":
                        variables[var_name] = float(var_cell.result)
                    else:
                        variables[var_name] = 0.0
                except Cell.DoesNotExist:
                    raise serializers.ValidationError(
                        f"Variable cell '{var_name}' not found"
                    )

            try:
                for var_name, var_value in variables.items():
                    formula = formula.replace(var_name, str(var_value))

                result = eval(formula)

                validated_data["result"] = str(result)

            except Exception as e:
                raise serializers.ValidationError(str(e))

        else:
            validated_data["result"] = value

        return super().create(validated_data)


class CellUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cell
        fields = ["value"]


class SheetSerializer(serializers.Serializer):
    cells = CellSheetSerializer(many=True, read_only=True)


class SheetCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sheet
        fields = ["sheet_id"]
