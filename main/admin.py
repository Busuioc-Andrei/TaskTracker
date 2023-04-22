from django.contrib import admin

from main.models import Issue, Project, Board, Column, ColorLabel


@admin.register(Project)
class IssueAdmin(admin.ModelAdmin):
    pass


@admin.register(Board)
class IssueAdmin(admin.ModelAdmin):
    pass


@admin.register(Column)
class IssueAdmin(admin.ModelAdmin):
    pass


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    pass


@admin.register(ColorLabel)
class IssueAdmin(admin.ModelAdmin):
    pass
