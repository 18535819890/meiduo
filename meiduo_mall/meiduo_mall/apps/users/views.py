from random import randint
from django_redis import get_redis_connection
from django.shortcuts import render
from threading import Thread
from rest_framework import status
from rest_framework.views import APIView
from meiduo_mall.libs.yuntongxun.sms import CCP
from users.models import User
from rest_framework.response import Response
from celery_tasks.sms_code.tasks import send_sms_code


# Create your views here.
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
