from random import randint
from django.conf import settings
from django_redis import get_redis_connection
from django.shortcuts import render
from threading import Thread
from rest_framework import status
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.views import APIView
from goods.models import SKU
from meiduo_mall.libs.yuntongxun.sms import CCP
from users.models import User
from rest_framework.response import Response
from celery_tasks.sms_code.tasks import send_sms_code
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from itsdangerous import TimedJSONWebSignatureSerializer as TJS
from users.serializers import CreateUserSerializer, UserDetailSerializer, EmailSeraizlizers, SKUHistoriesSerialzier, \
    SKUListSerialzier
from rest_framework_jwt.views import ObtainJSONWebToken

# Create your views here.
from users.utils import merge_cart_cookie_to_redis


class Sms_View(APIView):
    def get(self, request, mobile):
        # 获取手机号
        print(mobile)
        # 判断请求间隔，是否在60s内
        coon = get_redis_connection('sms_code')
        flag = coon.get('sms_code_flag_%s' % mobile)
        if flag:
            return Response({"error": "请求过于频繁"}, status=status.HTTP_400_BAD_REQUEST)
        # 生成短信验证码
        sms_code = '%06d' % randint(0, 999999)
        print(sms_code)
        # 保存到reids
        pl = coon.pipeline()  # 生成管道对象
        pl.setex('sms_code_%s' % mobile, 300, sms_code)
        pl.setex('sms_code_flag_%s' % mobile, 60, 'flag')
        pl.execute()
        # 发送短信
        send_sms_code.delay(mobile, sms_code)

        # ccp=CCP()
        # ccp.send_template_sms(mobile,[sms_code,'5'],1)
        # 异步发送短信
        # t=Thread(target='send_sms_code',kwargs={'mobile':mobile,'sms_code':sms_code})
        # t.start()
        # 返回结果
        return Response({"message": "ok"})


class User_View(APIView):
    """
        判断用户名号
    """

    def get(self, request, username):
        # 获取参数,正则匹配
        # 查询数据库中name所对应数据对象的数量
        count = User.objects.filter(username=username).count()
        # 返回结果
        return Response({
            'count': count
        })


class Mobile_View(APIView):
    """
         判断手机号
     """

    def get(self, request, mobile):
        # 获取mobile,正则匹配
        # 查询数据库中mobile所对应数据对象的数量
        count = User.objects.filter(mobile=mobile).count()
        # 返回结果
        return Response({
            'mobile': mobile,
            'count': count,
        })


class Users_View(CreateAPIView):
    serializer_class = CreateUserSerializer


class UserDetailView(RetrieveAPIView):
    """
        获取用户信息
    """
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class EmailView(UpdateAPIView):
    """
        更新邮箱
    """
    serializer_class = EmailSeraizlizers

    # 重写方法，按照指定对象返回
    def get_object(self):
        return self.request.user


class EmailVerifyView(APIView):
    def get(self, request):
        # 1.获取数据
        token = request.query_params.get("token", None)
        if token is None:
            return Response({"errors": "token不存在"}, status=400)
        # 2.验证数据,解密
        tjs = TJS(settings.SECRET_KEY, 300)
        try:
            data = tjs.loads(token)
        except:
            return Response({"error": "token无效"}, status=400)
        # 3、获取⽤户名
        username = data["name"]
        # 4、通过⽤户名查询数据对象
        user = User.objects.get(username=username)
        # 5、更新邮箱验证状态
        user.email_active = True
        user.save()
        # 6、返回结果
        return Response({
            "message": "ok"
        })


class SKUHistoriesView(CreateAPIView):
    """
        保存用户浏览历史记录
    """
    serializer_class = SKUHistoriesSerialzier

    def get(self, request):
        # 1、获取用户对象
        user = request.user
        # 2、查询redis中sku——id
        conn = get_redis_connection("history")
        sku_ids = conn.lrange("history_%s" % user.id, 0, 6)
        # 3、通过sku——id查询数据对象
        skus = SKU.objects.filter(id__in=sku_ids)
        # 4、序列化返回
        ser = SKUListSerialzier(skus, many=True)
        return Response(ser.data)


class UserAuthorizeView(ObtainJSONWebToken):
    """
    用户认证
    """
    def post(self, request, *args, **kwargs):
        # 调用父类的方法，获取drf jwt扩展默认的认证用户处理结果
        response = super().post(request, *args, **kwargs)

        # 仿照drf jwt扩展对于用户登录的认证方式，判断用户是否认证登录成功

        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = serializer.object.get('user') or request.user
            # 如果用户登录认证成功，则合并购物车
            response = merge_cart_cookie_to_redis(request,response,user)

        return response