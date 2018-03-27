# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse,JsonResponse
from common import models
import json,calendar
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
def logIn(request):
    return render(request, 'LogIn.html')


def signIn(request):
    if request.session.get('login',False)==True:
        schools = models.SchoolInfo.objects.filter(schoolresper=request.session.get('userid','1'))
        schoolGis = toDicts(schools)
        schoolGis.append(getUsername(request))
        schoolGisJ = json.dumps(schoolGis)
        return render(request, 'Mainmenu.html', {'gis_info': schoolGisJ})
    else:
        username=request.POST.get('inputUsername','')
        password=request.POST.get('inputPassword','')
        user=models.User.objects.filter(name=username)
        if user[0] != None:
             if user[0].name==username and user[0].userpassword==password:
                request.session['login']=True
                request.session['username'] = user[0].name
                request.session['userid'] = user[0].id
                schools=models.SchoolInfo.objects.filter(schoolresper=user[0].userid)
                schoolGis=toDicts(schools)
                schoolGis.append(getUsername(request))
                schoolGisJ=json.dumps(schoolGis)
                return render(request,'Mainmenu.html',{'gis_info':schoolGisJ})
        return render(request,'LogIn.html',{'error':'密码错误'})

#对象转化Json数据
def toDicts(objs):
        obj_arr=[]
        for o in objs:
            obj_arr.append(o.toDict())
        return obj_arr


def mapToSchool(request):
    schoolname=request.GET.get('schoolname')
    print schoolname
    school=models.SchoolInfo.objects.filter(schoolname=schoolname)
    Dict = {u'schoolid':school[0].schoolid}
    return JsonResponse(Dict)


def deviceInfoInit(request):
    schoolInfo=[]
    schools=models.SchoolInfo.objects.filter(schoolresper__exact=request.session.get('userid'))
    for school in schools:
        schoolInfo.append(school.getSchoolName())
    schoolInfo.append(getUsername(request))
    return render(request, 'DeviceInfoInit.html', {'initInfo':json.dumps(schoolInfo)})
#统计信息查看界面
def summary(request):
    schools = models.SchoolInfo.objects.filter(schoolresper=1)
    Info=[]
    for school in schools:
        Info.append(school.getSchoolName())
    Info.append(getUsername(request))
    return render(request,'SchoolSt.html',{'schoolInfo':json.dumps(Info)})
def deviceInfo(request,school_id):
    request.session['school_id'] = school_id
    deviceData=[]
    devicetypes = models.DeviceType.objects.all()
    for devicetype in devicetypes:
        deviceData.append(devicetype.getTypeName())
    deviceData.append(getUsername(request))
    return  render(request, 'DeviceInfo.html', {'detailsInfo':json.dumps(deviceData)})
#设备查看界面
def deviceStateCheck(request, device_id):
    request.session['device_id'] = device_id
    device = models.DeviceInfo.objects.filter(deviceid=device_id)
    Dict = device[0].toDict()
    return render(request, 'logIn/sum_line.html', {'device': json.dumps(Dict)})
#学校设备种类选择
def schoolDeviceAS(request):
    q = request.GET.get('devicetype')  # 获取参数
    schoolid=request.session.get('schoolid',0)
    devices = models.Device.objects.filter(schoolid=schoolid,typeid=q)
    school = models.SchoolInfo.objects.filter(schoolid=schoolid)
    devicename=models.DeviceType.objects.filter(typeid=q)
    ala_num=0
    usi_num=0
    lei_num=0
    jun_num=0
    for device in devices:
            if device.status==1:
                usi_num=usi_num+1
            elif device.status==2:
                lei_num=lei_num+1
            elif device.status==3:
                ala_num=ala_num+1
            elif device.status==4:
                jun_num=jun_num+1
    Dict={u'schoolname':school[0].schoolname,u'devicename':devicename[0].typename,u'alarm': ala_num,
          u'using': usi_num,u'leisure':lei_num ,u'junked':jun_num, }
    ans=json.dumps(Dict)
    return HttpResponse(ans)
#设备数据选择
def getDeviceLine(request):
    ans=[]
    deviceid=request.GET.get('deviceid')
    request.session['device_id']=deviceid
    hours=[0,0,0,0,0,0,0,0,0,0,0,0]
    months=["1月","2月","3月","4月","5月","6月","7月","8月","9月","10月","11月","12月"]
    devices=models.DeviceUseRecord.objects.filter(deviceid=deviceid)
    years=devices[0].getYears()
    for i in range(0,12):
        a=i+1
        data1=models.DeviceUseRecord.objects.filter(deviceid=deviceid,endtime__year=years[0],endtime__month=a)
        if data1!=None:
                for hour in data1:
                    hours[i]=((hour.endtime-hour.begintime).seconds)/3600+hours[i]
        else:
                hours[i]=0
    time={u'newdata':hours,u'newlabel':months,u'year':years}
    deviceDetails=models.DeviceInfo.objects.filter(deviceid=deviceid)
    ans.append(time)
    ans.append(deviceDetails[0].getDeviceDetail())
    return HttpResponse(json.dumps(ans))
def getDeviceLineAjax(request):
    year=request.GET.get('year')
    month=request.GET.get('month')
    print year
    print month
    if month=='0':
        hours=[0,0,0,0,0,0,0,0,0,0,0,0]
        label=["1月","2月","3月","4月","5月","6月","7月","8月","9月","10月","11月","12月"]
        for i in range(0,12):
            a=i+1
            data1=models.DeviceUseRecord.objects.filter(deviceid=request.session.get('device_id'),endtime__year=year,endtime__month=a)
            if data1!=None:
                for hour in data1:
                    hours[i]=((hour.endtime-hour.begintime).seconds)/3600+hours[i]
            else:
                hours[i]=0
    else:
        monthint=int(month)
        days=calendar.mdays[monthint]
        label=[]
        hours=[]
        for i in range(1,days):
            label.append(i)
            hours.append(0)
            data1 = models.DeviceUseRecord.objects.filter(deviceid=request.session['device_id'], endtime__year=year,
                                                     endtime__month=monthint,endtime__day=i)
            if data1 != None:
                for hour in data1:
                    hours[i-1] = ((hour.endtime - hour.begintime).seconds)/ 3600 + hours[i-1]
            else:
                hours[i-1] = 0
    ans={u'newdata':hours,u'newlabel':label}
    return HttpResponse(json.dumps(ans))
#获取用户名
def getUsername(request):
    username=request.session.get('username','')
    return{u'username':username}
def getDeviceType(request):
    q = request.GET.get('schoolid')  # 获取参数
    request.session['schoolid']=q
    devices=models.DeviceType.objects.all()
    devicetype=[]
    for device in devices:
        devicetype.append(device.getTypeName())
    ans=json.dumps(devicetype)
    return HttpResponse(ans)
def getDevices(request):
    q = request.GET.get('devicetype')  # 获取参数
    devicedetails = []
    if q !='0':
        devices=models.DeviceInfo.objects.filter(devicekind=q)
        for device in devices:
            devicedetails.append(device.getDeviceDetails())
        return HttpResponse(json.dumps(devicedetails))
    else:
        devices = models.DeviceInfo.objects.all()
        for device in devices:
            devicedetails.append(device.getDeviceDetails())
        return HttpResponse(json.dumps(devicedetails))
#登出
def logout(request):
    try:
        del request.session['user_id']
    except KeyError:
        pass
    return HttpResponse("You're logged out.")

 # --------------------------------admin related-----------------------------#
def alter(request):
    name=request.POST.get('devicename')
    devicename1=models.DeviceType.objects.get(filter=name)
    devicename2=devicename1.id
    number=request.POST.get('number')
    univalence=request.POST.get('univalence')
    sensorid=request.POST.get('sensorid')
    schoolid=request.POST.get('schoolid')
    checkerid=request.POST.get('checkerid')
    checkername = request.POST.get('checkername')
    status = request.POST.get('status', 3)
    if number is None or univalence is None:
        info = models.DeviceInfo.objects.all()
        dtype = models.DeviceType.objects.all()
        return render(request, 'admin_page.html', {'info': info, 'dtype': dtype})
    else:
        info = models.DeviceInfo.objects.all()
        dtype = models.DeviceType.objects.all()
        yy=models.Device.objects.create(number=number,univalence=univalence,schoolid=schoolid,sensorid=sensorid,checkerid=checkerid,typeid=devicename2,status=status,checkername=checkername)
        yy.save()

        return render(request,'admin_page.html',{'info':info,'dtype':dtype})

def dele(request):
    infolist = request.POST.getlist('checkbox1')
    print infolist
    for info in infolist:
        information = models.Device.objects.get(number=info)
        information.status=1
        information.save()
    for infos in infolist:
        infoss=models.DeviceInfo.objects.get(devicenum=infos)
        infoss.delete()
    dtype = models.DeviceType.objects.all()
    info = models.Device.objects.all()
    return render(request, 'admin_page.html', {'info': info,'dtype':dtype})

@csrf_exempt
def alter2(request):
    loginid = request.POST.get('login_id')
    password = request.POST.get('password')
    username =request.POST.get('username')
    usertype =request.POST.get('usertype')
    school1 =request.POST.get('school')
    email =request.POST.get('email')
    telephonenum =request.POST.get('tel')
    weixin =request.POST.get('weichat')
    qq =request.POST.get('qq')
    authorityname =request.POST.get('authorityname')
    authoritycode =request.POST.get('authoritycode')
    if loginid is None or  password is None:
        dtype = models.DeviceType.objects.all()
        info = models.Device.objects.all()
        return render(request, 'admin_page.html', {'detype': dtype, 'info': info})
    else :
        a=models.User.objects.create(loginid=loginid,password=password,username=username,usertype=usertype,school=school1,email=email,telephonenum=telephonenum,weixin=weixin,qq=qq)
        a.save()
        b = models.Authority.objects.create(authorityname=authorityname, authoritycode=authoritycode, usertype=usertype)
        b.save()
        dtype = models.DeviceType.objects.all()
        info = models.Device.objects.all()
        return render(request, 'admin_page.html', {'detype': dtype, 'info': info})
@csrf_exempt


def alter4(request):
    typename = request.POST.get('typename')

    if typename is None :
        dtype = models.DeviceType.objects.all()
        info = models.Device.objects.all()
        return render(request, 'admin_page.html', {'dtype': dtype, 'info': info})
    else:
       a = models.DeviceType.objects.create(typename=typename)
       a.save()
       dtype = models.DeviceType.objects.all()
       info = models.Device.objects.all()
    return render(request,'admin_page.html',{'dtype':dtype,'info':info})

def admin_page(request):
    dtype = models.DeviceType.objects.all()
    info = models.Device.objects.all()
    return render(request,'admin_page.html',{'dtype':dtype,'info':info})

def school(request):
    schoolname = request.POST.get('schoolname')
    schoolregister = request.POST.get('schoolregister')
    schoolstatus = request.POST.get('schoolstatus')
    schoolresper = request.POST.get('schoolresper')
    schooltel = request.POST.get('schooltel')
    if schoolname is None:
        dtype = models.DeviceType.objects.all()
        info = models.Device.objects.all()
        return render(request,'admin_page.html', {'dtype': dtype, 'info': info})
    else :
        a=models.SchoolInfo.objects.create(schoolname=schoolname,schoolregister=schoolregister,schoolstatus =schoolstatus,schoolresper=schoolresper,schooltel=schooltel )
        a.save()
        dtype = models.DeviceType.objects.all()
        info = models.Device.objects.all()
        return render(request, 'admin_page.html', {'dtype': dtype, 'info': info})
def room(request):
    schoolid=request.POST.get('schoolid')
    building=request.POST.get('building')
    roomname=request.POST.get('roomname')
    if schoolid is None:
        dtype = models.DeviceType.objects.all()
        info = models.Device.objects.all()
        return render(request, 'admin_page.html', {'dtype': dtype, 'info': info})
    else:
        a=models.RoomInfo.objects.create(schoolid=schoolid,building=building,roomname=roomname)
        a.save()
        dtype = models.DeviceType.objects.all()
        info = models.Device.objects.all()
        return render(request, 'admin_page.html', {'dtype': dtype, 'info': info})

@csrf_exempt
def getDeviceInfo(request):
    devices = models.DeviceInfo.objects.all().order_by("id")
    device = devices[0:99]
    obj_arr=[]
    for dv in device:
        d = dv.format()
        #获取设备类型名
        Type = models.DeviceType.objects.get(pk = dv.typeid)
        typename = Type.typename
        d["TypeId"] = typename
        #获取房间名
        Room = models.RoomInfo.objects.get(pk = dv.roomid)
        roomname = Room.building+" "+Room.roomname
        d["RoomId"] = roomname
        #获取使用状态
        if d["UseFlag"]== 1:
            d["UseFlag"]="（正在使用）"
        else:
            d["UseFlag"] = "（未使用）"
        #添加设备类型图片的静态地址
        d["imgUrl"] = "http://192.168.1.20:9999/static/img/"+str(dv.typeid)+".jpg"
        obj_arr.append(d)
    return HttpResponse(json.dumps(obj_arr))

@csrf_exempt
def getRoomInfo(request):
    roominfo=models.RoomInfo.objects.all()
    obj_arr = []
    building=[]
    for rm in roominfo:
        if not rm.building in building:
             building.append(rm.building)
    for bd in building:
        d={}
        d["building"]=bd
        room=models.RoomInfo.objects.filter(building=bd)
        f = []
        for rm in room:
           e = {}
           e["roomname"]=rm.roomname
           f.append(e)
        d["room"]=f
        obj_arr.append(d)
    return HttpResponse(json.dumps(obj_arr))

@csrf_exempt
def getDevice(request):
    schoolid=request.POST.get("schoolid")
    devices = models.DeviceInfo.objects.all().order_by("id")
    devicetype = models.DeviceType.objects.all()
    roominfo_Building = models.RoomInfo.objects.filter(schoolid=schoolid)
    for b in roominfo_Building:
        c = models.RoomInfo.objects.filter(building=b.building)
    device = devices[0:99]
    obj_arr=[]
    for dv in device:
        d = dv.format()
        #获取设备类型名
        Type = models.DeviceType.objects.get(pk = dv.typeid)
        typename = Type.typename
        d["TypeId"] = typename
        #获取房间名
        Room = models.RoomInfo.objects.get(pk = dv.roomid)
        roomname = Room.building+" "+Room.roomname
        d["RoomId"] = roomname
        #获取使用状态
        if d["UseFlag"]== 1:
            d["UseFlag"]="（正在使用）"
        else:
            d["UseFlag"] = "（未使用）"
        #添加设备类型图片的静态地址
        d["imgUrl"] = "http://192.168.1.20:9999/static/img/"+str(dv.typeid)+".jpg"
        obj_arr.append(d)
    return HttpResponse(json.dumps(obj_arr))