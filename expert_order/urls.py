from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from expert_order import views

urlpatterns = [
    url(r'^publish/$', views.PublishOrderView.as_view(), name='publish'),
    url(r'^orders/$', views.OrdersView.as_view(), name='available'),
    url(r'^detail/(?P<pk>[0-9]+)/$', views.OrderDetailView.as_view(), name='detail'),
    url(r'^update/(?P<pk>[0-9]+)/$', views.OrderUpdateView.as_view(), name='update'),
    url(r'^delete/(?P<pk>[0-9]+)/$', views.OrderDeleteView.as_view(), name='delete'),
    url(r'^pick/(?P<pk>[0-9]+)/$', views.PickOrderView.as_view(), name='pick'),
    url(r'^finish/(?P<pk>[0-9]+)/$', views.FinishOrderView.as_view(), name='finish'),
    url(r'^evaluate/(?P<pk>[0-9]+)/$', views.EvaluateView.as_view(), name='evaluate'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
