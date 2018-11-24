from django.conf import settings
from rest_framework import serializers
from django_redis import get_redis_connection
from users.models import User
import re
from rest_framework_jwt.settings import api_settings
from django.core.mail import send_mail
from celery_tasks.email.tasks import send_email
from itsdangerous import TimedJSONWebSignatureSerializer as TJS
class CreateUserSerializer(serializers.ModelSerializer):
    #显示模型类中没有的字段
    password2=serializers.CharField(max_length=20,min_length=8,write_only=True)
    allow=serializers.CharField(write_only=True)
    sms_code=serializers.CharField(max_length=6,min_length=6,write_only=True)
    class Meta:
        model=User
        fields=("username","password","mobile","password2","allow","sms_code","id")
        #添加额外的参数
        extra_kwargs={
            "password":{
                "write_only":True,
                "max_length":20,
                "min_length":8,
            },
            "username":{
                "max_length": 20,
                "min_length": 5,
            }
        }

    #单一字段的验证，手机号
    def  validate_mobile(self, value):
        if not re.match(r"^1[3-9]\d{9}$",value):
            raise serializers.ValidationError("手机格式错误")

        return value

    #多字段的验证
    def validate(self, attrs):

        # 协议的状态判断
        if attrs["allow"] != 'true':
            raise serializers.ValidationError("必须勾选协议")

        #密码比对
        if attrs["password"] != attrs['password2']:
            raise serializers.ValidationError("两次密码不一致")

        # 短信验证码比对
        #获取redis中的验证码
        conn=get_redis_connection("sms_code")
        rel_sms_code=conn.get('sms_code_%s'%attrs["mobile"])
        #判断是否过期
        if not rel_sms_code:
            raise serializers.ValidationError("验证码过期")
        #比对
        if attrs["sms_code"] != rel_sms_code.decode():
            raise serializers.ValidationError("两次验证码不一致")

        return attrs

    def create(self, validated_data):

        # 模型类数据保存
        user=User.objects.create_user(username=validated_data["username"],password=validated_data['password'],
                                 mobile=validated_data['mobile'])
        # jwt加密
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        user.token=token

        return user

class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=("username","mobile","email","email_active","default_address")



class EmailSeraizlizers(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=("email",)


    def update(self, instance, validated_data):

        instance.email=validated_data["email"]
        instance.save()

        # 加密用户数据
        data={"name":instance.username}
        tjs=TJS(settings.SECRET_KEY,300)
        token=tjs.dumps(data).decode()
        # verify_url = "http://www.meiduo.site:8080/success_verify_email.html?token="+token
        # subject="美多商城验证邮箱"
        # html_message='<p>尊敬的用户您好！</p>' \
        #                '<p>感谢您使用美多商城。</p>' \
        #              '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
        #              '<p><a href="%s">%s<a></p>' % (validated_data['email'], verify_url, verify_url)

        # send_mail(subject,'',settings.EMAIL_FROM,[validated_data["email"]],html_message=html_message)
        # 发送短信
        send_email.delay(token, validated_data["email"])
        return instance