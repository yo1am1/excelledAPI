from django.db import models


class Sheet(models.Model):
    id = models.AutoField(primary_key=True, unique=True, auto_created=True)
    sheet_id = models.CharField(max_length=100, unique=True, default=None)
    cells = models.ManyToManyField("Cell", related_name="cells", blank=True)

    def __str__(self):
        return self.sheet_id


class Cell(models.Model):
    cell_id = models.CharField(max_length=100, unique=True, default=None)
    sheet = models.ForeignKey(Sheet, on_delete=models.CASCADE, related_name="sheets")
    value = models.CharField(max_length=100)
    result = models.CharField(max_length=100, blank=True, null=True, default=None)

    def __str__(self):
        return self.cell_id
