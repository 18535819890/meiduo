from random import randint
from django_redis import get_redis_connection
from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from meiduo_mall.libs.yuntongxun.sms import CCP
from users.models import User
from rest_framework.response import Response

class Sms_View(APIView):
    def get(self,request,mobile):
        #获取手机号
        #生成短信验证码
        sms_code='%06d'%randint(0,999999)
        #保存到reids
        coon=get_redis_connection('sms_code')
        coon.setex('sms_code_%s'%mobile,300,sms_code)

        #发送短信
        ccp=CCP()
        ccp.send_template_sms(mobile,[sms_code,'5'],1)
        #返回结果
        return Response({"message":"ok"})