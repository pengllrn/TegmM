# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from common import models
from django.http import HttpResponse
import json



def index(request):
    if request.session.get('login', False) == True:
        # 判断用户类别

        return render(request,'Mainmenu.html')
    else:
        return render(request, 'LogIn.html')

def login(request):
    username = request.POST.get('inputUsername')
    password = request.POST.get('inputPassword')
    user1 = models.User.objects.filter(loginid=username, password=password)
    if len(user1) > 0:
        if user1[0].loginid == username and user1[0].password == password:
            request.session['login', False] = True
            request.session['user_id'] = user1[0].id
            request.session['user_type'] = user1[0].usertype
            user = user1[0].usertype
            if user == 1:
                dtype = models.DeviceType.objects.all()
                info = models.Device.objects.all()
                return render(request, 'devicehome.html', {'dtype': dtype, 'info': info, 'user': user})
            elif user == 2:
                # 需要的信息

                return render(request, 'Mainmenu.html')

    else:
        return HttpResponse(json.dumps({'error': "error"}))

