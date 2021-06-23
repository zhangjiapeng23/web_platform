from datetime import timedelta

from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from rest_framework.authtoken.models import Token
from rest_framework import generics
from rest_framework import permissions
from rest_framework.response import Response
from django.http import Http404
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework import status


from mobile_QA_web_platform.settings.base import TOKEN_EXPIRE
from .forms import UserCreateForm, UserLoginForm
from .models import UserInfo
from mobile_QA_web_platform.settings.base import LOCAL_HOST as host
from mobile_QA_web_platform.settings.base import LOCAL_PORT as port
from mobile_QA_web_platform.settings.base import MEDIA_URL
from .serializers import UserInfoSerializer, MoreTokenObtainPairSerializer, CreateUserSerializer, \
    MoreTokenRefreshSerializer, ModifyPasswordSerializer


class Profile(generics.GenericAPIView):

    queryset = UserInfo.objects.all()
    serializer_class = UserInfoSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        accounts = self.get_queryset()
        user = accounts.filter(pk=request.user.nid).first()
        if user:
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        raise Http404

    def put(self, request, *args, **kwargs):
        accounts = self.get_queryset()
        user = accounts.filter(pk=request.user.nid).first()
        if user:
            serializer = self.get_serializer(user, data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Http404


class Login(TokenObtainPairView):

    serializer_class = MoreTokenObtainPairSerializer


class RefreshToken(TokenRefreshView):

    serializer_class = MoreTokenRefreshSerializer


class ModifyPassword(generics.GenericAPIView):

    queryset = UserInfo.objects.all()
    serializer_class = ModifyPasswordSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def put(self, request):
        accounts = self.get_queryset()
        user = accounts.filter(pk=self.request.user.nid).first()
        if user:
            serializer = self.get_serializer(user, request.data)
            serializer.user = user
            if serializer.is_valid(raise_exception=True):
                return Response(status=status.HTTP_202_ACCEPTED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Http404


class Register(generics.CreateAPIView):

    queryset = UserInfo.objects.all()
    serializer_class = CreateUserSerializer



@require_POST
def register(request):
    response = {
        'code': 'register failed',
        'data': {
            'result': {},
            'error': {}
        }
    }
    form = UserCreateForm(request.POST, request.FILES)
    if not form.is_valid():
        response['data']['error'] = form.errors
    else:
        username = form.cleaned_data.get('username')
        password = make_password(form.cleaned_data.get('password'))
        user_logo = form.cleaned_data.get('logo')
        email = form.cleaned_data.get('email')
        register_user = UserInfo()
        register_user.username = username
        register_user.password = password
        if user_logo:
            register_user.logo = user_logo
        register_user.email = email
        register_user.save()
        response['code'] = 'register success'
    return JsonResponse(response)


@require_POST
def login_view(request):
    response = {
        'code': 'login failed',
        'data': {
            'result': {},
            'error': {}
        }
    }
    form = UserLoginForm(request.POST)
    if not form.is_valid():
        response['data']['error'] = form.errors
        return JsonResponse(response)
    username = form.cleaned_data.get('username')
    password = form.cleaned_data.get('password')
    user = authenticate(username=username, password=password)
    if user is not None:
        # login(request, user)
        try:
            token_obj = Token.objects.get(user_id=user.nid)
            # judge the token is or not expire
            if timezone.now() > (token_obj.created + timedelta(seconds=TOKEN_EXPIRE)):
                token_obj.delete()
                raise Exception
        except Exception:
            token_obj = Token.objects.create(user=user)

        token = token_obj.key
        response['code'] = 'login success'
        response['data']['result']['token'] = token
        response['data']['result']['username'] = user.username
        response['data']['result']['email'] = user.email
        response['data']['result']['is_superuser'] = user.is_superuser
        response['data']['result']['logo'] = host + ':' + port + MEDIA_URL + str(user.logo)
        return JsonResponse(response)

    else:
        response['data']['error'] = {'message': ['Username or password is invalid']}
    return JsonResponse(response)


@require_POST
def logout_view(request):
    response = {
        'code': 'logout success',
        'data': ""
    }
    token = request.META.get('HTTP_AUTHORIZATION')
    if token:
        key = token.split(' ')[1]
        try:
            token_obj = Token.objects.get(key=key)
            token_obj.delete()
        except Exception:
            response['code'] = 'logout failed'
    else:
        response['code'] = 'logout failed'
        response['data'] = 'miss token'
    return JsonResponse(response)


