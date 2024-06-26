from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class tasks(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    task_name = models.CharField(max_length=50, null=True)
    task_start_time = models.TimeField()
    task_end_time = models.TimeField()
    task_date = models.DateField()
    task_description = models.TextField(default='Task description here.....')
    completed = models.BooleanField(default=False)
    def __str__(self) -> str:
        return f"{self.task_name}"