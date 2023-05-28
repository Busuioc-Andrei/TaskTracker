from main.models import Project, Board, Invitation


def navbar(request):
    current_project = None
    user = request.user
    if request.user.is_authenticated:
        current_project = request.user.profile.current_project
    return {
        "project_list": Project.filter_visible_items(user),
        "board_list": Board.objects.filter(project=current_project),
        "current_project": current_project,
        "invitation_list": Invitation.objects.filter(sent_to=request.user, accepted=None)
    }