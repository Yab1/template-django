from django.contrib.auth import authenticate, login, logout
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed, NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from core.api.mixins import ApiAuthMixin

from .selectors import user_get_login_data


class LoginApi(APIView):
    """
    Following https://docs.djangoproject.com/en/5.0/topics/auth/default/#how-to-log-a-user-in
    """

    class InputSerializer(serializers.Serializer):
        email = serializers.EmailField()
        password = serializers.CharField()

    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(request, **serializer.validated_data)

        if user is None:
            raise AuthenticationFailed("Invalid login credentials. Please try again or contact support.")

        login(request, user)

        session_key = request.session.session_key

        return Response(
            data={
                "session": session_key,
            },
        )


class LogoutApi(ApiAuthMixin, APIView):
    def get(self, request):
        logout(request)

        return Response(data={"message": "The user has been logged out successfully."})


class MeApi(ApiAuthMixin, APIView):
    def get(self, request):
        try:
            data = user_get_login_data(current_user=request.user)

            return Response(
                data={
                    "data": data,
                },
            )

        except NotFound as e:
            raise NotFound(e)
        except Exception as e:
            return Response({"message": "An unexpected error occurred", "extra": {"details": str(e)}}, status=500)
