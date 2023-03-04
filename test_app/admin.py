from django.contrib import admin

from test_app.models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    pass
