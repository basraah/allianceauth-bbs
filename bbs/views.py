from django.shortcuts import render
from django.views import View
from django.urls import reverse_lazy
from django.views.generic import UpdateView, DeleteView, CreateView, TemplateView
from django.views.generic.detail import SingleObjectMixin
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.http.response import HttpResponseForbidden, Http404

from . import models, forms

import logging

logger = logging.getLogger(__name__)


class BaseBbsView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'bbs.access_forum'


class BaseCreateView(CreateView):
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class BaseUpdateView(UpdateView):
    def form_valid(self, form):
        # Check the user is allowed to edit this item
        if (self.object.created_by == self.request.user
           or self.request.user.has_perm('bbs.moderator')
           or self.request.user.is_superuser):
            return super().form_valid(form)
        raise HttpResponseForbidden


class CategoryView(BaseBbsView, TemplateView, SingleObjectMixin):
    template_name = 'bbs/list_topics.html'
    model = models.Category

    def get(self, request, *args, **kwargs):
        context = {}
        if 'pk' in kwargs:
            logger.debug('Loading category id %s', kwargs['pk'])
            category = self.get_object()
            context['category'] = category
            if not category.user_can_view(request.user):
                raise HttpResponseForbidden
            topics = category.topics.all()
        else:
            logger.debug('Loading all categories')
            categories = self.get_queryset().visible_for_user(request.user).values_list('pk', flat=True)
            topics = models.Topic.objects.filter(category__pk__in=categories)
            logger.debug('Got %s topics', len(topics))
        context['topics'] = topics\
            .select_related('created_by__profile__main_character')\
            .prefetch_related('posts', 'posts__created_by__profile__main_character')
        return self.render_to_response(context)


class BaseTopicView(BaseBbsView):
    model = models.Topic


class TopicView(BaseTopicView, TemplateView, SingleObjectMixin):
    template_name = 'bbs/view_topic.html'

    def get(self, request, *args, **kwargs):
        topic_qs = self.get_queryset()\
            .select_related('created_by__profile__main_character',
                            'category')\
            .prefetch_related('posts',
                              'posts__created_by__profile__main_character')
        topic = self.get_object(topic_qs)
        topic.views += 1
        topic.save()
        return self.render_to_response({'topic': topic, 'form': forms.PostForm()})


class TopicCreate(BaseTopicView, BaseCreateView, SingleObjectMixin):
    form_class = forms.TopicForm

    @property
    def success_url(self):
        return reverse_lazy('bbs:topic-view', kwargs={'pk': self.object.pk})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class TopicUpdate(BaseTopicView, BaseUpdateView, SingleObjectMixin):
    form_class = forms.TopicForm


class BasePostView(BaseBbsView):
    model = models.Post


class PostCreate(BasePostView, BaseCreateView, SingleObjectMixin):
    form_class = forms.PostForm

    @property
    def success_url(self):
        return reverse_lazy('bbs:topic-view', kwargs={'pk': self.object.topic_id})

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.topic_id = self.request.resolver_match.kwargs.get('topic_id')
        return super().form_valid(form)


class PostUpdate(BasePostView, BaseUpdateView, SingleObjectMixin):
    form_class = forms.PostForm
