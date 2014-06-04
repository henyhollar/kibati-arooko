from rest_framework import permissions

class IsUplink(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has a `plug id` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:            
            return False

        # Instance must have an attribute named `owner`.
        if request.path.find('unplug-user'):
            try:
                return obj.plug.id == request.user.id
            except:
                return False

        elif request.path.find('plug-user') and request.user.permission=='uplink':
            return True
