from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from expert_skill import views

app_name = 'skill'

urlpatterns = [
    url(r'^categories/$', views.CategoriesView.as_view(), name='categories'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
