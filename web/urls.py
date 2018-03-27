#coding=utf-8
from django.conf.urls import url
from web import views as web

urlpatterns = [
    url(r'^index/$', web.logIn),
]