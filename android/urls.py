# coding=utf-8
import android.views as av
from django.conf.urls import url

urlpatterns = [
    url(r'^getdeviceinfo/$', av.getDeviceInfo),
    url(r'^getdevice/$', av.get_school_building_room),
    url(r'^getdevicedetail/$', av.get_detail_device),
    url(r'^damageapply/$', av.device_damage_apply),
    url(r'^dealdamage/$', av.deal_damage),
    url(r'^gis/$', av.gis),
    url(r'^login/$', av.user_login),
    url(r'^schoollist/$', av.school_list),
    url(r'^search/$', av.search),
    url(r'^showapplylist/$', av.show_apply_list),
    url(r'^statistics/$', av.statistics),
    url(r'^static/(/d+.jpg)',av.getDeviceInfo),
]