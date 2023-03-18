from main.models import Project, Board


def navbar(request):
    return {
        "project_list": Project.objects.all(),
        "board_list": Board.objects.all()
    }