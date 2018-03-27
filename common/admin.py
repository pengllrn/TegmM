# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from . import models
import sys
import hashlib
reload(sys)
sys.setdefaultencoding('utf-8')
# Register your models here.

from .models import User,SchoolInfo,SeniorUser,UserType

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    # ----------------------------------------列表预设----------------------------------------- #

    # ----------------------------------------列表属性----------------------------------------- #
    list_display = ['username', 'loginid', 'usertype', 'school', 'regist_time', 'status']  # 显示列表
    list_filter = ['regist_time']  # 过滤字段,显示在右边，快速过滤
    search_fields = ['username']  # 搜索，显示在上边，根据什么字段
    list_per_page = 10  # 每10条分页

    # ----------------------------------------添加、修改页属性----------------------------------------- #

    # 添加、修改页属性
    # 这两个只能同时出现一个
    # fields = []         #显示的先后顺序
    fieldsets = [
        ("基本信息", {"fields": ['loginid', 'password','username']}),
        ("用户类别", {"fields": ['usertype','job','school']}),
        ("其他信息", {"fields": ['email', 'telephonenum', 'weixin','qq']}),
        ("注册时间", {"fields": ['regist_time','status']})
    ]
    # ----------------------------------------基本操作----------------------------------------- #
    def save_model(self, request, obj, form, change):
        obj.password = hashlib.md5(obj.password).hexdigest()
        if obj.usertype !=None:
            if obj.usertype.pk == 4:
                return
        if obj.school !=None:
            if obj.school.pk == 1:
                return
        obj.save()

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super(UserAdmin, self).get_search_results(request, queryset, search_term)
        if search_term != "":
            return queryset, use_distinct
        queryset = self.model.objects.exclude(official = True)
        return queryset,use_distinct

@admin.register(SchoolInfo)
class SchoolAdmin(admin.ModelAdmin):
    # ----------------------------------------列表属性----------------------------------------- #
    list_display = ['schoolname','registnum','province','city','county','regist_time','schoolstatus']
    list_filter = ['province','city','county',]  # 过滤字段,显示在右边，快速过滤
    search_fields = ['schoolname']  # 搜索，显示在上边，根据什么字段
    # ----------------------------------------添加、修改页属性----------------------------------------- #
    fieldsets = [
        ("基本信息", {"fields": ['schoolname', 'registnum', 'schoollinkman']}),
        ("地理位置", {"fields": ['province', 'city', 'county','longitude','latitude']}),
        ("注册时间", {"fields": ['regist_time','schoolstatus']})
    ]
    # ----------------------------------------基本操作----------------------------------------- #
    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super(SchoolAdmin, self).get_search_results(request, queryset, search_term)
        if search_term != "":
            return queryset, use_distinct
        queryset = self.model.objects.exclude(pk=1)
        return queryset,use_distinct

@admin.register(SeniorUser)
class SeniorUserAdmin(admin.ModelAdmin):
    # ----------------------------------------列表属性----------------------------------------- #
    list_display = ['username', 'loginid','rank', 'regist_time', 'isdelete']  # 显示列表
    list_filter = ['regist_time']  # 过滤字段,显示在右边，快速过滤
    search_fields = ['username']  # 搜索，显示在上边，根据什么字段
    list_per_page = 10  # 每10条分页
    filter_horizontal = ['schools']

    # ----------------------------------------添加、修改页属性----------------------------------------- #

    # 添加、修改页属性
    # 这两个只能同时出现一个
    # fields = []         #显示的先后顺序
    fieldsets = [
        ("基本信息", {"fields": ['loginid', 'password', 'username']}),
        ("管辖学校", {"fields": ['rank','schools']}),
        ("其他信息", {"fields": ['email', 'telephonenum', 'weixin', 'qq']}),
        ("注册时间", {"fields": ['regist_time','isdelete']})
    ]
    # ----------------------------------------基本操作----------------------------------------- #
    def save_model(self, request, obj, form, change):
        loginid = obj.loginid
        password = hashlib.md5(obj.password).hexdigest()
        username = obj.username
        job = obj.rank
        official = True
        email = obj.email
        telephonenum = obj.telephonenum
        weixin = obj.weixin
        qq = obj.qq
        regist_time = obj.regist_time
        status = True
        usertype = UserType.objects.get(pk = 4)
        school =SchoolInfo.objects.get(pk = 1)
        user = models.User.objects.create(loginid=loginid,password=password,username=username,
                                          usertype = usertype,school = school,
                                          job=job,official=official,email=email,telephonenum=telephonenum,
                                          weixin=weixin,qq=qq,regist_time=regist_time,status=status)
        user.save()
        obj.password = hashlib.md5(obj.password).hexdigest()
        obj.save()



