from django.db import models


class Department(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.TextField()  # This field type is a guess.
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True,db_column='parent_id')
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        #managed = False
        db_table = 'Department'


class Employee(models.Model):
    id = models.BigAutoField(primary_key=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, blank=True, null=True)
    full_name = models.TextField()
    position = models.TextField()
    hired_at_field = models.DateField(db_column='hired_at ', blank=True, null=True)  # Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        #managed = False
        db_table = 'Employee'
