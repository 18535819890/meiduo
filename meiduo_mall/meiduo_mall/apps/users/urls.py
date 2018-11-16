from . import views
from django.conf.urls import url
urlpatterns=[
    url(r"^sms_codes/(?P<mobile>1[3-9]\d{9})/$",views.Sms_View.as_view()),
    url(r"^usernames/(?P<username>\w+)/count/$",views.User_View.as_view()),
    url(r"^mobiles/(?P<mobile>\d+)/count/$",views.Mobile_View.as_view()),
]