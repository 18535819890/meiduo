# from django.conf.urls import url
# from . import views
#
# from rest_framework.routers import DefaultRouter
# urlpatterns=[
#     url(r"^categories/(?P<pk>\d+)/$",views.CategoriesView.as_view()),
#     url(r"^categories/(?P<pk>\d+)/skus/$", views.GoodsSkuView.as_view()),
#
# ]
#
# router=DefaultRouter()
# router.register('skus/search',views.SKUSearchView,base_name='skus_search')
# urlpatterns+=router.urls

from django.conf.urls import url
from django.contrib import admin
from rest_framework.routers import DefaultRouter
from . import views
urlpatterns = [
    url(r'^categories/(?P<pk>\d+)/$', views.CategoriesView.as_view()),
    url(r'^categories/(?P<pk>\d+)/skus/$', views.GoodsSkuView.as_view()),
]
router=DefaultRouter()
router.register('skus/search', views.SKUSearchView, base_name='skus_search')
urlpatterns += router.urls