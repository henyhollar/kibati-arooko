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
    url(r'^postmans/', include('postman.urls')),
    url(r'^registers/$', views.RegisterList.as_view(), name='register-list'),
    url(r'^registerSlaves/(?P<slave>[0-9]{11})/$', views.RegisterSlaveList.as_view(), name='register-slave-list'),
    url(r'^changePasswords/(?P<username>[0-9]{11})/$', views.ChangePassword.as_view(), name='change-password'),
    url(r'^resets/(?P<username>[0-9]{11})/$', views.ResetPassword),
    url(r'^users/(?P<username>[0-9]{11})/$', views.UserDetail.as_view(), name='register-detail'),
    url(r'^glueUsers/(?P<master_username>[0-9]{11})/(?P<username>[0-9]{11})/$', views.GlueUser.as_view(), name='glue-user-detail'),
    url(r'^unglueUsers/(?P<username>[0-9]{11})/$', views.GlueUser.as_view(), name='unglue-user-detail'),
    url(r'^changeDefaults/(?P<username>[0-9]{11})/$', views.ChangeDefault.as_view(), name='change-default-detail'),


)

from uplink import views

urlpatterns += patterns('',
    url(r'^uplinkRegisters/(?P<uplink_username>[0-9]{11})/$', views.UplinkRegisterList.as_view(), name='uplink-register-list'),
    url(r'^plugUsers/(?P<uplink_username>[0-9]{11})/(?P<username>[0-9]{11})/$', views.PlugUser.as_view(), name='plug-user-detail'),
    url(r'^unplugUsers/(?P<username>[0-9]{11})/$', views.PlugUser.as_view(), name='unplug-user-detail'),
)

from wallet import views

urlpatterns += patterns('',
    url(r'^uplinkDownlinkWalletUpdates/(?P<uplink_username>[0-9]{11})/(?P<owner>[0-9]{11})/$', views.UpdateWallet.as_view(), name='uplink-update-wallet-detail'),
    url(r'^selfWalletUpdates/(?P<owner>[0-9]{11})/$', views.UpdateWallet.as_view(), name='self-update-wallet-detail'),
    url(r'^masterSlaveWalletUpdates/(?P<master_username>[0-9]{11})/(?P<owner>[0-9]{11})/$', views.UpdateWallet.as_view(), name='master-slave-wallet-detail'),

    url(r'^uplinkDownlinkOfflinewalletUpdates/(?P<uplink_username>[0-9]{11})/(?P<owner>[0-9]{11})/$', views.UpdateOfflineWallet.as_view(), name='uplink-update-wallet-detail'),
    url(r'^selfOfflinewalletUpdates/(?P<owner>[0-9]{11})/$', views.UpdateOfflineWallet.as_view(), name='self-update-wallet-detail'),
    url(r'^masterSlaveOfflinewalletUpdates/(?P<master_username>[0-9]{11})/(?P<owner>[0-9]{11})/$', views.UpdateOfflineWallet.as_view(), name='master-slave-wallet-detail'),
)

from scheduler import views

urlpatterns += patterns('',
    url(r'^schedules/(?P<username>[0-9]{11})/$', views.Scheduler.as_view(), name='schedule-detail'),
)


from twilioService import views

urlpatterns += patterns('',
    url(r'^calls/$', views.Call.as_view(), name='call-detail'),
)

from bankService import views

urlpatterns += patterns('',
    url(r'^gtbPays/$', views.gtPay),
)

urlpatterns = format_suffix_patterns(urlpatterns)


from wallet.utils import mail_handler

urlpatterns += patterns('',
    url(r'^mails/$', mail_handler),
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
   url(r'^recharges/(?P<username>[0-9]{11})/$', views.Recharge.as_view()),
)