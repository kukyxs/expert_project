import os
import time

from PIL import Image
from django.contrib.auth.models import User
from django.db.models import Avg
from rest_framework import permissions, renderers, parsers, authentication, status, generics, mixins
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.views import APIView

from expert_order.models import Order
from expert_project import settings
from expert_user.models import ExUser
from expert_user.serializers import RegisterSerializer, ResetPassSerializer, UploadAvatarSerializer, \
    UserInformationSerializer, UserInformationModifiedSerializer


# 注册
class RegisterView(APIView):
    throttle_classes = ()
    authentication_classes = ()
    permission_classes = (permissions.AllowAny,)
    renderer_classes = (renderers.JSONRenderer,)
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)

    def post(self, request, format='json'):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = User(username=request.data['username'], password=request.data['password'])
            user.set_password(user.password)
            user.save()
            ExUser.objects.filter(user=user).update(phone_num=request.data['phone_num'])
            return Response({"code": 200, "message": "Register Succeed"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 登录
class LoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            return Response({"code": 200, "id": user.id, "username": user.username, "token": token.key},
                            status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 密码重置
class ResetPasswordView(APIView):
    throttle_classes = ()
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    renderer_classes = (renderers.JSONRenderer,)
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)

    def put(self, request, format='json'):
        serializer = ResetPassSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            user.set_password(request.data['new_password'])
            User.objects.filter(id=user.id).update(password=user.password)
            return Response({"code": 200, "message": "Reset Password Succeed"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 头像修改
class UploadAvatarView(APIView):
    throttle_classes = ()
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    renderer_classes = (renderers.JSONRenderer,)
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser, parsers.FileUploadParser,)

    def post(self, request, format='json'):
        serializer = UploadAvatarSerializer(data=request.data)
        if serializer.is_valid():
            # 时间戳作为头像的名称
            name = str(time.time()).split(".")[0].strip()
            # 获取后缀名
            suffix = request.data['suffix'].split('\"')[1].strip()
            # 拼接头像名称
            avatar_name = "avatar/{}/{}.{}".format(request.user.username, name, suffix)
            avatar = Image.open(request.data['avatar'])

            # 创建副本保存文件
            if not os.path.exists('media/avatar/' + request.user.username):
                os.makedirs('media/avatar/' + request.user.username)

            # 拼接头像路径
            avatar_path = os.path.join(settings.MEDIA_ROOT, avatar_name).replace("\\", "/")
            avatar.save(avatar_path)
            # 更新数据库数据
            ExUser.objects.filter(user=request.user).update(avatar=avatar_path)
            return Response({"code": 200, "avatar": avatar_path}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 获取用户信息
class GetUserInformationView(generics.RetrieveAPIView):
    queryset = ExUser.objects.all()
    serializer_class = UserInformationSerializer
    throttle_classes = ()
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    renderer_classes = (renderers.JSONRenderer,)
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser, parsers.FileUploadParser,)

    def get(self, request, *args, **kwargs):
        # 插入平均值
        avg_grade = Order.objects.filter(picker_id=kwargs.get('pk')).aggregate(avg_grade=Avg('grade')).get('avg_grade')
        if avg_grade:
            ExUser.objects.filter(id=kwargs.get('pk')).update(avg_grade=avg_grade)
        return super(GetUserInformationView, self).retrieve(self, request, *args, **kwargs)


# 修改用户信息
class UserInformationModifiedView(APIView):
    throttle_classes = ()
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    renderer_classes = (renderers.JSONRenderer,)
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser, parsers.FileUploadParser,)

    def put(self, request, format='json'):
        try:
            ex_user = ExUser.objects.get(user=request.user)
        except ExUser.DoesNotExist:
            return Response({"code": 400, "message": ""}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserInformationModifiedSerializer(ex_user, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
