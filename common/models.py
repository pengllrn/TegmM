# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

import time
# Create your models here.

# ----------------------------------------用户表----------------------------------------- #
class User(models.Model):
    loginid = models.CharField(db_column='login_id', max_length=40, blank=True, null=True,verbose_name="登录账号")  # 用户账号
    password = models.CharField(db_column='password', max_length=40, blank=True, null=True,verbose_name="登录密码")  # 用户密码
    username = models.CharField(db_column='username', max_length=10, blank=True, null=True,verbose_name="姓名")  # 用户姓名
    usertype = models.ForeignKey("UserType",db_column='usertype',null=True,verbose_name="用户类型")  # 用户类型
    job = models.CharField(db_column='job', max_length=20, blank=True, null=True, verbose_name="工作")  # 工作
    school = models.ForeignKey("SchoolInfo",db_column='school', blank=True, null=True,verbose_name="所属学校")  # 所属学校
    isOfficial = models.BooleanField(db_column='isOfficial', default=False,verbose_name="是否是校级以上的用户")  # 是否是校级以上的用户
    email = models.EmailField(db_column='email', blank=True, null=True,verbose_name="Email")  # Email
    telephonenum = models.CharField(db_column='tel', max_length=20,blank=True, null=True,verbose_name="电话")  # Tel
    weixin = models.CharField(db_column='wechat', max_length=20, blank=True, null=True,verbose_name="微信")  # 微信
    qq = models.CharField(db_column='qq', max_length=20, blank=True, null=True,verbose_name="QQ")  # QQ
    status = models.BooleanField(db_column='status', default=True,verbose_name="状态")  # 是否有效
    regist_time = models.DateTimeField(db_column='regist_time',verbose_name="注册时间")  #注册时间

    def __str__(self):
        return self.username
    class Meta:
        db_table = 'User'
        verbose_name_plural = "普通用户"
    def getuserinfo(self):
        return {u'userid':self.id,"username":self.username,"usertype":self.usertype,u'job':self.job,'school':self.school,
                'isOfficial':self.isOfficial,'regist_time':self.regist_time.strftime("%y-%m-%d"),
                'email':self.email,'wechat':self.weixin,'qq':self.qq}

# ----------------------------------------高级用户表（多校查看用户）----------------------------------------- #
# 说明：与User表中的official字段对应，此表用于超级管理员添加用户
class SeniorUser(models.Model):
    loginid = models.CharField(db_column='login_id', max_length=40, blank=True, null=True,verbose_name="登录账号")  # 用户账号
    password = models.CharField(db_column='password', max_length=40, blank=True, null=True,verbose_name="登录密码")  # 用户密码
    username = models.CharField(db_column='username', max_length=10, blank=True, null=True,verbose_name="姓名")  # 用户姓名
    rank = models.CharField(db_column='rank',max_length=20, blank=True, null=True,verbose_name="职位")  # 职位
    email = models.EmailField(db_column='email', blank=True, null=True,verbose_name="Email")  # Email
    telephonenum = models.CharField(db_column='tel', max_length=20,blank=True, null=True,verbose_name="电话")  # Tel
    weixin = models.CharField(db_column='wechat', max_length=20, blank=True, null=True,verbose_name="微信")  # 微信
    qq = models.CharField(db_column='qq', max_length=20, blank=True, null=True,verbose_name="QQ")  # QQ
    isdelete = models.BooleanField(db_column='status', default=True,verbose_name="是否有效")  # 是否已经被删除
    regist_time = models.DateTimeField(db_column='regist_time',verbose_name="注册时间")  #注册时间

    schools = models.ManyToManyField("SchoolInfo", db_column="schoolid", verbose_name="学校")

    def __str__(self):
        return u'%s(%s)' % (self.username,self.rank)
    class Meta:
        db_table = 'SeniorUser'
        verbose_name_plural = "地区官员"


# ----------------------------------------用户类型表----------------------------------------- #
class UserType(models.Model):
    typename = models.CharField(db_column='typename',max_length=20)
    def __str__(self):
        return self.typename
    class Meta:
        db_table = 'usertype'


class Device(models.Model):
    number = models.CharField(db_column='Number',max_length=20,blank=True,null=True) #设备编号(可能不唯一)
    typeid = models.ForeignKey("DeviceType",db_column="TypeId",blank=True,null=True)  #设备类型id
    univalence = models.FloatField(db_column='Univalence',blank=True,null=True)  #设备单价
    sensorid = models.IntegerField(db_column='SensorId',blank=True, null=True)  # 传感器的编号
    schoolid = models.IntegerField(db_column='SchoolId',blank=True,null=True)  #学校id
    checkerid = models.IntegerField(db_column="CheckerId",blank=True,null=True) #检查人，负责人编号
    checkername = models.CharField(db_column='CheckerName',max_length=20,blank=True,null=True) #负责人的名字
    status = models.IntegerField(db_column="Status",default=4) #设备状态 1删除 2 报废 3 正常 4 库存

    regist_first=models.DateTimeField(db_column="regist_first",blank=True,null=True)#第一次登记的时间
    use_depart=models.CharField(db_column="use_depart",max_length=20,blank=True,null=True)#使用部门

    def format2(self):
        return {u'devicenum':self.number,u'type':self.typeid,u'sensorid':self.sensorid,u'status':self.status,
                u"schoolname":self.schoolid,u'usedepart':self.use_depart,u'checkid':self.checkerid,
                u'checkname':self.checkername,u'regist_first':self.regist_first.strftime("%Y-%m-%d")}

    class Meta:
        db_table = 'Device'

class DeviceInfo(models.Model):
    deviceid = models.IntegerField(db_column="DeviceId", blank=True, null=True)  # 设备ID
    devicenum = models.CharField(db_column='DeviceNum', max_length=20, blank=True, null=True)  # 设备的编号
    schoolid = models.IntegerField(db_column='SchoolId', blank=True, null=True)  # 学校id
    typeid = models.IntegerField(db_column="TypeId", blank=True, null=True)  # 设备类型id
    roomid = models.CharField(db_column='RoomId', max_length=20, blank=True, null=True)  #房间ID
    ordernum = models.IntegerField(db_column='OrderNum', blank=True, null=True)  # 设备在房间里的序号
    devicekind = models.CharField(db_column='DeviceKind',max_length=50,blank=True,null=True)  #设备型号
    description = models.TextField(db_column='Description',blank=True,null=True)  #设备描述
    configureinfo = models.CharField(db_column='ConfigureInfo',max_length=30,blank=True,null=True)  #配置信息
    useflag = models.BooleanField(db_column="UseFlag",blank=True)  #使用状态
    max_use_time=models.IntegerField(db_column="max_use_time",blank=True,null=True)#日最长使用时间

    def __str__(self):
        return self.id
    def format(self):
        return {u'DeviceId':self.deviceid,u'TypeId':self.typeid,u'DeviceNum':self.devicenum,u'RoomId':self.roomid,
                u'OrderNum':self.ordernum,u'UseFlag':self.useflag}
    def format2(self):
        return {u'useflag':self.useflag,u'order':self.ordernum,u'devicekind':self.devicekind,u'description':self.description,
                u'configureinfo':self.configureinfo}

    class Meta:
        db_table = 'DeviceInfo'

class DeviceGis(models.Model):
    longitude = models.FloatField(db_column='Longitude',blank=True,null=True)  #经度
    latitude = models.FloatField(db_column='Latitude',blank=True,null=True)  #维度
    deviceid = models.IntegerField(db_column="DeviceId",blank=True,null=True)  #设备ID
    devicenum = models.CharField(db_column='DeviceNum', max_length=20, blank=True, null=True)  # 设备编号
    schoolid = models.IntegerField(db_column='SchoolId', blank=True, null=True)  # 学校id

    class Meta:
        db_table = 'DeviceGis'

class DeviceAlarm(models.Model):
    deviceid = models.IntegerField(db_column="DeviceId", blank=True, null=True)  # 设备ID
    devicenum = models.CharField(db_column='DeviceNum', max_length=20, blank=True, null=True)  # 设备编号
    schoolid = models.IntegerField(db_column='SchoolId',blank=True, null=True)  # 学校id
    roomid = models.IntegerField(db_column='RoomId',blank=True, null=True) #房间ID
    ordernum = models.IntegerField(db_column='OrderNum',blank=True, null=True)  #设备在房间里的序号
    alarmstart = models.BooleanField(db_column='AlarmStart',blank=True)  #设备是否处于报警状态

    class Meta:
        db_table = 'DeviceAlarm'

class DeviceUseRecord(models.Model):
    deviceid = models.IntegerField(db_column="DeviceId", blank=True, null=True)  # 设备ID
    schoolid = models.IntegerField(db_column='SchoolId',blank=True, null=True)  # 学校id
    existimage = models.BooleanField(db_column='ExistImage',blank=True)  #是否有图像
    imageaddress = models.CharField(db_column='ImageAddress', max_length=40,blank=True, null=True)  # 图片地址
    date = models.DateField(db_column="date", blank=True, null=True)  # 使用的时间
    begintime = models.DateField(db_column='BeginTime',blank=True, null=True)  #设备开始使用的时间
    endtime = models.DateField(db_column='EndTime',blank=True, null=True)  #设备结束使用的时间

    class Meta:
        db_table = 'DeviceUseRecord'

#设备使用频率表
class DeviceUseRate(models.Model):
    deviceid = models.IntegerField(db_column="DeviceId", blank=True, null=True)  # 设备ID
    date = models.DateField(db_column="date",blank=True,null=True) #使用的时间
    #date = models.CharField(db_column="date",max_length=20,blank=True,null=True)  #使用的时间
    rate = models.FloatField(db_column="rate",blank=True,null=True) #使用率

    def format(self):
        return {u'date':self.date.strftime("%m-%d"),u'rate':self.rate}

    class Meta:

        db_table = 'DeviceUseRate'

class DeviceToSensor(models.Model):
    sensornum = models.CharField(db_column='SensorNum', max_length=50, blank=True, null=True)  # 传感器的编号

    class Meta:
        db_table = 'DeviceToSensor'

class DeviceType(models.Model):
    #typeid = models.IntegerField(db_column="TypeId", blank=True, null=True)  # 设备类型id
    school = models.IntegerField(db_column="school",blank=True,null=True) #学校
    typename = models.CharField(db_column="TypeName",max_length=30,blank=True,null=True)  #设备名称

    def __str__(self):
        return u"%s " % (self.typename)

    def format(self):
        return {u'typename':self.typename}

    class Meta:
        db_table = "DeviceType"

# ----------------------------------------学校信息表----------------------------------------- #
class SchoolInfo(models.Model):
    schoolname = models.CharField(db_column='school_name',max_length=40,verbose_name="学校")  #学校名字
    registnum = models.CharField(db_column="registnum",max_length=50,blank=True,null=True,verbose_name="注册号")  #学校的注册号
    schoollinkman = models.ForeignKey("User",db_column="school_linkman",blank=True,null=True,verbose_name="负责人")  #学校负责人id
    province = models.CharField(db_column="province",max_length=20,blank=True,null=True,verbose_name="省")  #省
    city = models.CharField(db_column="city", max_length=20, blank=True, null=True,verbose_name="市")  # 市
    county = models.CharField(db_column="county", max_length=20, blank=True, null=True,verbose_name="区/县")  # 区/县
    longitude = models.FloatField(db_column='longitude',blank=True,null=True,verbose_name="经度")  #学校的经度
    latitude = models.FloatField(db_column='latitude',blank=True,null=True,verbose_name="纬度")  #学校的纬度
    schoolstatus = models.BooleanField(db_column='school_status',default=True,verbose_name="状态")  #学校的状态
    regist_time = models.DateTimeField(db_column="regist_time",null=True,verbose_name="注册时间")
    def __str__(self):
        return u"%s %s-%s-%s" % (self.schoolname,self.province,self.city,self.county)
    class Meta:
        db_table = "SchoolInfo"
        verbose_name_plural = "学校"
    def format(self):
        return {u'schoolid':self.id,u'schoolname':self.schoolname,u'longitude':self.longitude,u'latitude':self.latitude}


class ViewRegion(models.Model):
    userid = models.IntegerField(db_column='userid',blank=True,null=True)  #用户id
    viewschool = models.IntegerField(db_column='view_school',blank=True,null=True)  #能查看学校的id

    class Meta:
        db_table = 'ViewRegion'

class PropertyDamage(models.Model):
    deviceid = models.IntegerField(db_column="DeviceId", blank=True, null=True)  # 设备ID
    applier = models.CharField(db_column='Applier',max_length=40,blank=True,null=True)  #申请人姓名
    applierid = models.IntegerField(db_column='ApplierId',blank=True,null=True) #申请人ID
    appliertel = models.TextField(db_column="ApplierTel",blank=True,null=True)  #申请人电话
    datetime = models.CharField(db_column='DateTime',max_length=40,blank=True,null=True)  #申述时间
    #以下是补充
    damagedepict=models.TextField(db_column='damage_depict',blank=True,null=True)   #设备损坏描述
    photo1=models.TextField(db_column='photo_1',blank=True,null=True)  #图片1
    photo2=models.TextField(db_column='photo_2',blank=True,null=True)  #图片2
    photo3=models.TextField(db_column='photo_3',blank=True,null=True)  #图片3
    photo4 = models.TextField(db_column='photo_4', blank=True, null=True)  # 图片4
    photo5 = models.TextField(db_column='photo_5', blank=True, null=True)  # 图片5
    photo6 = models.TextField(db_column='photo_6', blank=True, null=True)  # 图片6
    voice = models.TextField(db_column='voice',blank=True,null=True)  #声音
    ##第二次补充
    schoolid = models.IntegerField(db_column="schoolid",blank=True,null=True)  #学校ID
    devicenum = models.CharField(db_column="devicenum",max_length=30,blank=True,null=True)  #编号
    type = models.CharField(db_column='type',max_length=20,null=True,blank=True) #类型
    deal_status = models.IntegerField(db_column='deal_status',default="0") #处理状态0:未处理 1：已处理（同意） 2：已处理（拒绝） 3：已删除
    def format(self):
        return {u'deviceid':self.deviceid,u'devicenum':self.devicenum,u'name':self.applier,
                u'type':self.type,u"datetime":self.datetime,u'deal_status':self.deal_status}
    def format2(self):
        return {u'applier':self.applier,u'appliertel':self.appliertel,u'datetime':self.datetime,u'schoolid':self.schoolid,
                u'type':self.type,u'devicenum':self.devicenum,u'damagedepict':self.damagedepict,u'photo1':self.photo1,
                u'photo2': self.photo2,u'photo3':self.photo3,u'photo4':self.photo4,u'photo5':self.photo5,u'photo6': self.photo6}
    class Meta:
        db_table = "PropertyDamage"

class PropertyCheck(models.Model):
    deviceid = models.IntegerField(db_column="DeviceId", blank=True, null=True)  # 设备ID
    checkerid = models.CharField(db_column='CheckerId',max_length=40,blank=True,null=True)  #审核人ID
    checkername = models.CharField(db_column='CheckerName',max_length=40,blank=True,null=True) #审核人姓名
    checketime = models.DateField(db_column='CheckeTime',blank=True,null=True)  #审核时间
    checkerflag = models.BooleanField(db_column='CheckFlag',blank=True)  #审核结果

    class Meta:
        db_table = 'PropertyCheck'


class RoomInfo(models.Model):
    schoolid = models.IntegerField(db_column='SchoolId', blank=True, null=True)  # 学校id
    building = models.CharField(db_column='Building',max_length=50,blank=True,null=True)  #楼层名
    roomname = models.CharField(db_column='RoomName',max_length=50,blank=True,null=True)  #房间名

    def format(self):
        return {u'buildingname':self.building,u'roomname':self.roomname}

    class Meta:
        db_table = 'RoomInfo'
