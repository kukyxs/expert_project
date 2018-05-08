from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

from expert_user import views

urlpatterns = [
    url(r'^register/$', views.RegisterView.as_view(), name='register'),
    url(r'^login/$', views.LoginView.as_view(), name='login'),
    url(r'^reset_password/$', views.ResetPasswordView.as_view(), name='reset_password'),
    url(r'^upload_avatar/$', views.UploadAvatarView.as_view(), name='upload_avatar'),
    url(r'^get_info/(?P<pk>[0-9]+)/$', views.GetUserInformationView.as_view(), name='get_info'),
    url(r'^modified/$', views.UserInformationModifiedView.as_view(), name='modified'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
