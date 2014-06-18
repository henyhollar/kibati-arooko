from django.conf.urls import url, patterns, include
from register import views

from django.contrib import admin
from rest_framework.urlpatterns import format_suffix_patterns

admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'Tibaty_Arooko.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    #url(r'^api-auth/', include('rest_framework.urls',namespace='rest_framework')),
    url(r'^user-token/', 'rest_framework.authtoken.views.obtain_auth_token'),
    url(r'^user-session/$', views.SessionView.as_view()),
    url(r'^docs/', include('rest_framework_swagger.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^postman/', include('postman.urls')),
    url(r'^register/$', views.RegisterList.as_view(), name='register-list'),
    url(r'^register-slave/(?P<slave>[0-9]{11})/$', views.RegisterSlaveList.as_view(), name='register-slave-list'),
    url(r'^change-password/(?P<username>[0-9]{11})/$', views.ChangePassword.as_view(), name='change-password'),
    url(r'^reset/(?P<username>[0-9]{11})/$', views.ResetPassword ),
    url(r'^user/(?P<username>[0-9]{11})/$', views.UserDetail.as_view(), name='register-detail'),
    url(r'^user-info/(?P<username>[0-9]{11})/$', views.UserInformation.as_view(), name='user-information'),
    url(r'^glue-user/(?P<master_username>[0-9]{11})/(?P<username>[0-9]{11})/$', views.GlueUser.as_view(), name='glue-user-detail'),
    url(r'^unglue-user/(?P<username>[0-9]{11})/$', views.GlueUser.as_view(), name='unglue-user-detail'),
    url(r'^change-default/(?P<username>[0-9]{11})/$', views.ChangeDefault.as_view(), name='change-default-detail'),

)

from uplink import views

urlpatterns += patterns('',
    url(r'^uplink-register/(?P<uplink_username>[0-9]{11})/$', views.UplinkRegisterList.as_view(), name='uplink-register-list'),
    url(r'^plug-user/(?P<uplink_username>[0-9]{11})/(?P<username>[0-9]{11})/$', views.PlugUser.as_view(), name='plug-user-detail'),
    url(r'^unplug-user/(?P<username>[0-9]{11})/$', views.PlugUser.as_view(), name='unplug-user-detail'),
)

from wallet import views

urlpatterns += patterns('',
    url(r'^uplink-downlink-wallet-update/(?P<uplink_username>[0-9]{11})/(?P<owner>[0-9]{11})/$', views.UpdateWallet.as_view(), name='uplink-update-wallet-detail'),
    url(r'^self-wallet-update/(?P<owner>[0-9]{11})/$', views.UpdateWallet.as_view(), name='self-update-wallet-detail'),
    url(r'^master-slave-wallet-update/(?P<master_username>[0-9]{11})/(?P<owner>[0-9]{11})/$', views.UpdateWallet.as_view(), name='master-slave-wallet-detail'),
)

from scheduler import views

urlpatterns += patterns('',
    url(r'^schedule/(?P<username>[0-9]{11})/$', views.Scheduler.as_view(), name='schedule-detail'),
)


from twilioService import views

urlpatterns += patterns('',
    url(r'^call/$', views.Call.as_view(), name='call-detail'),
)

from bankService import views

urlpatterns += patterns('',
    url(r'^gtb-pay/$', views.gtPay),
)

urlpatterns = format_suffix_patterns(urlpatterns)


from wallet.utils import mail_handler

urlpatterns += patterns('',
    url(r'^mail/$', mail_handler),
)

from message.views import message

urlpatterns += patterns('',
    url(r'^message/$', message),
)

# The following urls will be used for synchronizing both platforms

from synchronize import views

urlpatterns += patterns('',
    url(r'^sync/$', views.sync),

)


from transaction import views

urlpatterns += patterns('',
   url(r'^action/$', views.agw),
)