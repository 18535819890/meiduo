from . import views
from django.conf.urls import url
urlpatterns=[
    url(r"sms_code/(?P<mobile>1[3-9]\d{9})/$",views.Sms_View.as_view())
]