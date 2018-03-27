# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

import time
from django import forms
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from common import models
import json
from itertools import chain

url = "http://192.168.1.82:9999"

icon_path = url + "static/img/"
damage_device_path = ""


@csrf_exempt
def user_login(request):
    user_id = request.POST.get("userid")
    password = request.POST.get("password")
    user = models.User.objects.filter(loginid=user_id,password=password,status=True)
    if len(user) > 0:
        if user[0].loginid == user_id and user[0].password == password:
            request.session['IS_LOGIN'] = True
            return HttpResponse(json.dumps(user[0].getuserinfo()))
    return HttpResponse("error")


def formatDicts(objs):
    obj_arr = []
    for o in objs:
        obj_arr.append(o.format())
    return obj_arr


@csrf_exempt
def getDeviceInfo(request):
    is_login = request.session.get("IS_LOGIN", True)
    if is_login:
        obj_json = {}
        devices = models.DeviceInfo.objects.all().order_by("id")
        obj_json["device"] = format_dev_info(devices)
        roominfo = models.RoomInfo.objects.all()
        obj_json["schoolbyid"] = format_room_info(roominfo)
        type = models.DeviceType.objects.all()
        obj_json["type"] = formatDicts(type)
        return HttpResponse(json.dumps(obj_json))


@csrf_exempt
def get_school_building_room(request):
    roominfo = models.RoomInfo.objects.all()
    obj_arr = []
    building = []
    for rm in roominfo:
        if not rm.building in building:
            building.append(rm.building)
    for bd in building:
        d = {}
        d["building"] = bd
        room = models.RoomInfo.objects.filter(building=bd)
        f = []
        for rm in room:
            e = {}
            e["roomname"] = rm.roomname
            f.append(e)
        d["room"] = f
        obj_arr.append(d)
    return HttpResponse(json.dumps(obj_arr))


@csrf_exempt
def get_detail_device(request):
    deviceid = request.POST.get("deviceid")
    if deviceid != None:
        device = models.Device.objects.get(pk=deviceid)
        dict1 = device.format2()
        deviceinfo = models.DeviceInfo.objects.get(deviceid=deviceid)
        dict2 = deviceinfo.format2()
        object_json = dict(dict1, **dict2)
        # 获取type
        type = models.DeviceType.objects.get(pk=device.typeid)
        object_json["type"] = type.typename
        # 获取sensor
        sensor = models.DeviceToSensor.objects.get(pk=device.sensorid)
        object_json["sensor"] = sensor.sensornum
        ##获取gis
        gis = models.DeviceGis.objects.get(deviceid=deviceid)
        object_json["gis"] = "(" + str(gis.latitude) + "," + str(gis.longitude) + ")"
        ##获取学校名字
        school = models.SchoolInfo.objects.get(pk=device.schoolid)
        object_json["schoolname"] = school.schoolname
        ##获取联系人电话
        person = models.User.objects.get(pk=device.checkerid)
        object_json["checktel"] = person.telephonenum
        ##获取10天的使用率
        userate = models.DeviceUseRate.objects.filter(deviceid=deviceid).order_by("date")
        if len(userate) > 10:
            userate_10 = userate[len(userate) - 10:len(userate)]
        else:
            userate_10 = userate[0:10]
        object_json["userate_10"] = formatDicts(userate_10)
        ##初始化平均使用率
        object_json['avgrate'] = "0"

        if object_json["status"] == 3:
            object_json["status"] = "正常"
        elif object_json["status"] == 2:
            object_json["status"] = "已报废"

        ##获取房间信息
        room = models.RoomInfo.objects.get(pk=deviceinfo.roomid)
        object_json['roominfo'] = room.format()
        # 获取使用状态
        if object_json["useflag"] == True:
            object_json["useflag"] = "正在使用"
        else:
            object_json["useflag"] = "未使用"
        return HttpResponse(json.dumps(object_json))
    return None


def format_dev_info(obj):
    device = obj[0:99]
    obj_arr = []
    for dv in device:
        d = dv.format()
        # 获取设备类型名
        Type = models.DeviceType.objects.get(pk=dv.typeid)
        typename = Type.typename
        d["TypeId"] = typename
        # 获取房间名
        Room = models.RoomInfo.objects.get(pk=dv.roomid)
        d["BuildName"] = Room.building
        d["RoomName"] = Room.roomname
        # 获取使用状态
        if d["UseFlag"] == 1:
            d["UseFlag"] = "正在使用"
        else:
            d["UseFlag"] = "未使用"
        # 添加设备类型图片的静态地址
        d["imgUrl"] = url + "/static/img/" + str(dv.typeid) + ".jpg"
        obj_arr.append(d)
    return obj_arr


def format_room_info(obj_roominfo):
    obj_arr = []
    building = []
    for rm in obj_roominfo:
        if not rm.building in building:
            building.append(rm.building)
    for bd in building:
        d = {}
        d["building"] = bd
        room = models.RoomInfo.objects.filter(building=bd)
        f = []
        for rm in room:
            e = {}
            e["roomname"] = rm.roomname
            f.append(e)
        d["room"] = f
        obj_arr.append(d)
    return obj_arr


@csrf_exempt
def device_damage_apply(request):
    if request.method == "POST":
        deviceid = request.POST.get("deviceid")
        records = models.PropertyDamage.objects.filter(deviceid=deviceid)
        if len(records) > 0:
            if records[0].deal_status !=2:
                return HttpResponse(json.dumps({"code": 0}))
            else:
                records.delete()
                records.save()
        applierid = request.POST.get("applierid")
        appliername = request.POST.get("appliername")
        damagedepict = request.POST.get("damagedepict")
        vocie = request.POST.get("voice")
        datetime = request.POST.get("datetime")
        num = [0, 1, 2, 3, 4, 5]
        photo = [None, None, None, None, None, None]
        for n in num:
            image = request.FILES.get('image' + str(n))
            if image == None:
                break
            else:
                f = open(".//TEGApp//static//damageapply_img//" + image.name, 'wb')
                for chunk in image.chunks(chunk_size=1024):
                    f.write(chunk)
                    photo[n] = url + "/static/damageapply_img/" + image.name
        if photo[0] != None and datetime != None:
            device = models.Device.objects.get(pk=deviceid)
            type = models.DeviceType.objects.get(pk=device.typeid)
            damagedevice = models.PropertyDamage.objects.create(deviceid=deviceid, applierid=applierid,
                                                                applier=appliername,datetime=datetime, damagedepict=damagedepict,
                                                                photo1=photo[0], photo2=photo[1], photo3=photo[2],
                                                                photo4=photo[3], photo5=photo[4], photo6=photo[5],
                                                                voice=vocie, devicenum=device.number,
                                                                schoolid=device.schoolid,type=type.typename)
            damagedevice.save()
            return HttpResponse(json.dumps({"code": 1}))
    return HttpResponse(json.dumps({"message": "System Error!", "code": -1}))


class UserForm(forms.Form):
    username = forms.CharField(max_length=50)
    headImg = forms.FileField()


@csrf_exempt
def deal_damage(request):
    type = request.POST.get("type")
    deviceid = request.POST.get("deviceid")
    d = {}
    if type == "1":
        damagedevice = models.PropertyDamage.objects.get(deviceid=deviceid)
        device = models.DeviceInfo.objects.get(deviceid=deviceid)
        room = models.RoomInfo.objects.get(pk=device.roomid)
        d = damagedevice.format2()
        d["room"] = room.building + "  " + room.roomname
        return HttpResponse(json.dumps(d))
    if type == "2":
        result = request.POST.get("result")
        if result == "pass":
            damagedevice = models.PropertyDamage.objects.get(deviceid=deviceid)
            damagedevice.deal_status = 1
            damagedevice.save()
            device = models.Device.objects.get(pk=deviceid)
            device.status = 2
            device.save()
            propertycheck = models.PropertyCheck.objects.create(deviceid=deviceid, checkerflag=True)
            propertycheck.save()
            return HttpResponse("success")
        else:
            damagedevice = models.PropertyDamage.objects.get(deviceid=deviceid)
            damagedevice.deal_status = 2
            damagedevice.save()
            propertycheck = models.PropertyCheck.objects.create(deviceid=deviceid, checkerflag=False)
            propertycheck.save()
    return HttpResponse(json.dumps(d))


@csrf_exempt
def show_apply_list(request):
    type = request.POST.get("type")
    obj_arr = []
    if type == "1":
        userid = request.POST.get("userid")
        damagelist = models.PropertyDamage.objects.filter(applierid=userid)
        if len(damagelist) > 0:
            for o in damagelist:
                d = o.format()
                if d["deal_status"] == 3:
                    d["deal_status"] = "已删除"
                elif d["deal_status"] == 2:
                    d["deal_status"] = "已处理(拒绝)"
                elif d["deal_status"] == 1:
                    d["deal_status"] = "已处理(同意)"
                elif d["deal_status"] == 0:
                    d["deal_status"] = "待处理"
                obj_arr.append(d)
    elif type == "2":
        school = request.POST.get("school")
        damagelist = models.PropertyDamage.objects.filter(schoolid=school, deal_status=0)
        if len(damagelist) > 0:
            obj_arr = formatDicts(damagelist)
    return HttpResponse(json.dumps(obj_arr))


@csrf_exempt
def gis(request):
    type = request.POST.get("type")
    obj_json = {}
    if type == "1":
        school = models.SchoolInfo.objects.all()
        obj_json["mSchoolLists"] = format_school_list(school)
    if type == "2":
        schoolid = request.POST.get("schoolid")
        buildings = models.RoomInfo.objects.filter(schoolid=schoolid)
        obj_json["mBuildingLists"] = format_building_list(buildings)
    if type == "3":
        schoolid = request.POST.get("schoolid")
        buildingname = request.POST.get("buildingname")
        rooms = models.RoomInfo.objects.filter(schoolid=schoolid)
        room = rooms.filter(building=buildingname)
        obj_json["mRoomLists"] = format_room_list(room)
    if type == "4":
        schoolid = request.POST.get("schoolid")
        buildingname = request.POST.get("buildingname")
        roomname = request.POST.get("roomname")
        room = models.RoomInfo.objects.filter(schoolid=schoolid, building=buildingname).get(roomname=roomname)
        devices = models.DeviceInfo.objects.filter(roomid=room.id)
        obj_json["device"] = format_dev_info(devices)
    return HttpResponse(json.dumps(obj_json))


@csrf_exempt
def search(request):
    schoolid = request.POST.get("schoolid")
    condition = request.POST.get("condition")
    obj_json = {}
    search1 = models.DeviceInfo.objects.filter(schoolid=schoolid, devicenum=condition)
    if len(search1) > 0:
        obj_json["device"] = format_dev_info(search1)
        return HttpResponse(json.dumps(obj_json))

    room = models.RoomInfo.objects.filter(schoolid=schoolid, roomname=condition)
    if len(room) > 0:
        search2 = models.DeviceInfo.objects.filter(roomid=room[0].id)
        obj_json["device"] = format_dev_info(search2)
    return HttpResponse(json.dumps(obj_json))


@csrf_exempt
def school_list(request):
    schoolid = request.POST.get("school")
    userid = request.POST.get("userid")
    if schoolid != "1":
        school = models.SchoolInfo.objects.filter(id=schoolid)
        return HttpResponse(json.dumps(format_school_list(school)))
    elif schoolid == "1":
        user = models.User.objects.get(pk=userid)
        schools = models.SeniorUser.objects.filter(regist_time=user.regist_time)
        return HttpResponse(json.dumps(format_school_list(schools)))


def format_school_list(obj):
    school = obj[0:99]
    obj_arr = []
    for sc in school:
        d = sc.format()
        # 获取设备总数
        devices = models.DeviceInfo.objects.filter(schoolid=sc.id)
        d["totaldevice"] = len(devices)
        usingdevice = devices.filter(useflag=True)
        d["usingdevice"] = len(usingdevice)
        if len(devices) != 0:
            d["rate"] = len(usingdevice) * 100 / len(devices)
        else:
            d["rate"] = 0
        obj_arr.append(d)
    return obj_arr


def format_building_list(obj):
    building = []
    obj_arr = []
    for o in obj:
        if not o.building in building:
            building.append(o.building)
    for bu in building:
        d = {}
        d["buildingname"] = bu
        rooms = models.RoomInfo.objects.filter(building=bu)
        total = 0
        using = 0
        for room in rooms:
            devices = models.DeviceInfo.objects.filter(roomid=room.id)
            total += len(devices)
            using += len(devices.filter(useflag=True))
        d["totaldevice"] = total
        d["usingdevice"] = using
        obj_arr.append(d)
    return obj_arr


def format_room_list(obj):
    obj_arr = []
    for o in obj:
        d = {}
        d["roomname"] = o.roomname
        devices = models.DeviceInfo.objects.filter(roomid=o.id)
        d["totaldevice"] = len(devices)
        d["usingdevice"] = len(devices.filter(useflag=True))
        obj_arr.append(d)
    return obj_arr


@csrf_exempt
def statistics(request):
    schoolid = request.POST.get("school")
    type = request.POST.get("type")
    obj_arr = []
    if type=="1":##采购
        devices = models.Device.objects.filter(schoolid=schoolid)
        devices = devices.exclude(status=1)
        obj_arr = getType(devices)

    elif type=="2":##库存
        devices = models.Device.objects.filter(schoolid=schoolid,status=4)
        obj_arr = getType(devices)

    elif type=="3":##价值
        devices = models.Device.objects.filter(schoolid=schoolid)
        devices = devices.exclude(status=1)
        typeid = []
        for dv in devices:
            if not dv.typeid in typeid:
                typeid.append(dv.typeid)
                d = {}
                d["typename"] = models.DeviceType.objects.get(id=dv.typeid).typename
                device = devices.filter(typeid=dv.typeid)
                to = 0
                for o in device:
                    to = to + o.univalence
                d["value"] = to
                obj_arr.append(d)

    elif type=="4":##报废
        devices = models.Device.objects.filter(schoolid=schoolid, status=2)
        obj_arr = getType(devices)

    return HttpResponse(json.dumps(obj_arr))

def getType(obj):
    typeid = []
    obj_arr = []
    for dv in obj:
        if not dv.typeid in typeid:
            typeid.append(dv.typeid)
            d = {}
            d["typename"] = models.DeviceType.objects.get(id=dv.typeid).typename
            d["value"] = len(obj.filter(typeid=dv.typeid))
            obj_arr.append(d)
    return obj_arr