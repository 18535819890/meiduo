from . import views
from rest_framework_jwt.views import obtain_jwt_token
from django.conf.urls import url
urlpatterns=[
    url(r"^sms_codes/(?P<mobile>1[3-9]\d{9})/$",views.Sms_View.as_view()),
    url(r"^usernames/(?P<username>\w+)/count/$",views.User_View.as_view()),
    url(r"^mobiles/(?P<mobile>\d+)/count/$",views.Mobile_View.as_view()),
    url(r"^users/$",views.Users_View.as_view()),
    url(r'^authorizations/$', obtain_jwt_token),


]