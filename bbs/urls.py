from django.conf.urls import url

from . import views

app_name = 'bbs'

urlpatterns = [
    url(r'^topic/(?P<pk>[0-9]+)/$', views.TopicView.as_view(), name='topic-view'),
    url(r'^topic/(?P<topic_id>[0-9]+)/reply/$', views.PostCreate.as_view(), name='post-create'),
    url(r'^topic/create/$', views.TopicCreate.as_view(), name='topic-create'),
    url(r'^post/(?P<pk>[0-9]+)/edit/$', views.PostUpdate.as_view(), name='post-edit'),
    url(r'^category/(?P<pk>[0-9]+)/$', views.CategoryView.as_view(), name='category'),
    url(r'^$', views.CategoryView.as_view(), name='categories'),
]
