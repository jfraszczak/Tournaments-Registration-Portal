from tournaments import views
from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static

app_name = 'tournaments'

urlpatterns = [
    url(r'^$', views.list_of_tournaments, name='list_of_tournaments'),
    url('register/$', views.register, name='register'),
    url('login/$', views.user_login, name='login'),
    url('logout/$', views.user_logout, name='logout'),
    url(r'activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.activate_account, name='activate'),
    url(r'reset_password/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.reset_password, name='reset_password'),
    url('forgot_password/$', views.forgot_password, name='forgot_password'),
    url('list_of_tournaments/$', views.list_of_tournaments, name='list_of_tournaments'),
    url('my_tournaments/$', views.my_tournaments, name='my_tournaments'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)