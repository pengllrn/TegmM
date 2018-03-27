#coding=utf-8
from django.conf.urls import url

from common import views as cv

urlpatterns = [
    url('^$',cv.index),
    url(r'^login/$', cv.login,name='login'),
]