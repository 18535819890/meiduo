from random import randint

from django.conf import settings
from django_redis import get_redis_connection
from django.shortcuts import render
from threading import Thread
from rest_framework import status
from rest_framework.generics import CreateAPIView,RetrieveAPIView,UpdateAPIView
from rest_framework.views import APIView
from meiduo_mall.libs.yuntongxun.sms import CCP
from users.models import User
from rest_framework.response import Response
from celery_tasks.sms_code.tasks import send_sms_code

from rest_framework.permissions import IsAuthenticated, IsAdminUser
from itsdangerous import TimedJSONWebSignatureSerializer as TJS
# Create your views here.
from users.serializers import CreateUserSerializer, UserDetailSerializer, EmailSeraizlizers


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
    def get(self,request,username):
        #获取参数,正则匹配
        #查询数据库中name所对应数据对象的数量
        count=User.objects.filter(username=username).count()
        #返回结果
        return Response({
            'count':count
        })

class Mobile_View(APIView):
    """
         判断手机号
     """
    def get(self,request,mobile):

        #获取mobile,正则匹配
        #查询数据库中mobile所对应数据对象的数量
        count=User.objects.filter(mobile=mobile).count()
        #返回结果
        return Response({
            'mobile':mobile,
            'count':count,
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
    def get(self,request):
        #1.获取数据
        token=request.query_params.get("token",None)
        if token is None:
            return Response({"errors":"token不存在"},status=400)
        #2.验证数据,解密
        tjs=TJS(settings.SECRET_KEY,300)
        try:
            data=tjs.loads(token)
        except:
            return Response({"error":"token无效"},status=400)
        # 3、获取⽤户名
        username=data["name"]
        # 4、通过⽤户名查询数据对象
        user=User.objects.get(username=username)
        # 5、更新邮箱验证状态
        user.email_active=True
        user.save()
        # 6、返回结果
        return Response({
            "message":"ok"
        })