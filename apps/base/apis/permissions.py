from django.views import View
from rest_framework.permissions import BasePermission
from rest_framework.request import Request


class AppOwnPermission(BasePermission):
    def has_permission(self, request: Request, view: View) -> bool:
        """Checks if App-Own key is in request header, App-Own key will be passed from internal requests.

        Parameters
        ----------
        request : Request
        view : View

        Returns
        -------
        bool
        """
        if "App-Own" in request.headers:
            return True
        return False
