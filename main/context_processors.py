from main.models import Project, Board


def navbar(request):
    current_project = None
    if request.user.is_authenticated:
        current_project = request.user.profile.current_project
    return {
        "project_list": Project.objects.all(),
        "board_list": Board.objects.filter(project=current_project),
        "current_project": current_project
    }