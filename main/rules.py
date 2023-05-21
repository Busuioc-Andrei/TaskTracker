import rules


@rules.predicate
def is_project_creator(user, project):
    return project.created_by == user


@rules.predicate
def check_parent_view_permission(user, obj):
    parent = getattr(obj, 'parent', None)
    if parent:
        return check_parent_view_permission(user, parent)
    return obj._meta.rules_permissions.get('view')(user, obj)


@rules.predicate
def check_parent_change_permission(user, obj):
    parent = getattr(obj, 'parent', None)
    if parent:
        return check_parent_change_permission(user, parent)
    return obj._meta.rules_permissions.get('change')(user, obj)


@rules.predicate
def check_parent_delete_permission(user, obj):
    parent = getattr(obj, 'parent', None)
    if parent:
        return check_parent_delete_permission(user, parent)
    return obj._meta.rules_permissions.get('delete')(user, obj)


@rules.predicate
def is_public(user, obj):
    return True


parent_rules_permissions = {
    "view": check_parent_view_permission,
    "change": check_parent_change_permission,
    "delete": check_parent_delete_permission,
}


# how it should work
# there needs to be a ProjectPermissionGroup
# the creator of the project is auto added to it
# he can invite other people to join the project
# one project has multiple groups
# a group has only one project
# all other objects that have parent as a parent (all of them)
# will need to bubble up to project to check perms

# a simple version which will be very similar to this would be with created_by
# how can a board check if the project is created by user?


# idea
# define a parent column
# and make a rule that checks the permission of the parent object
