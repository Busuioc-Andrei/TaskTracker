from main.models import Project


def projects(request):
    return {
        "project_list": Project.objects.all()
    }