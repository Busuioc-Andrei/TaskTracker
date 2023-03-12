from django.contrib import admin

from main.models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    pass
