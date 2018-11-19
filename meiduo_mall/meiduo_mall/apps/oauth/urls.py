from django.conf.urls import url
from . import views


urlpatterns=[
    url(r'^qq/authorization/$', views.QQauthURLView.as_view()),
    url(r'^qq/user/$', views.OauthView.as_view()),
]