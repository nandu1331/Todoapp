from django.contrib import admin
from .models import tasks

# Register your models here.
class mymodeladmin(admin.ModelAdmin):
    list_display = ["task_name","task_description","task_date","task_start_time","task_end_time"]


admin.site.register(tasks, mymodeladmin)
