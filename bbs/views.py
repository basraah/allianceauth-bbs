from django.views import View
from django.urls import reverse_lazy
from django.views.generic import UpdateView, DeleteView, CreateView, TemplateView
from django.views.generic.detail import SingleObjectMixin
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.http.response import HttpResponseForbidden
from django.utils.translation import ugettext_lazy as _

from . import models, forms

import logging

logger = logging.getLogger(__name__)


class BaseBbsView(View, LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return True

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        user_test_result = self.get_test_func()()
        if not user_test_result:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class BaseCreateView(CreateView):
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def handle_no_permission(self):
        return redirect('bbs:categories')


class BaseUpdateView(UpdateView):
    def form_valid(self, form):
        # Check the user is allowed to edit this item
        if (self.object.created_by == self.request.user
           or self.request.user.has_perm('bbs.moderator')
           or self.request.user.is_superuser):
            return super().form_valid(form)
        raise HttpResponseForbidden

    def handle_no_permission(self):
        return redirect('bbs:categories')


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

    def get_queryset(self):
        return super().get_queryset()\
            .select_related('created_by__profile__main_character',
                            'category')\
            .prefetch_related('posts',
                              'posts__created_by__profile__main_character')

    def get(self, request, *args, **kwargs):
        topic = self.get_object()
        topic.views += 1
        topic.save()
        return self.render_to_response({'topic': topic, 'form': forms.PostForm()})

    def test_func(self):
        logger.debug('has_permission?')
        return self.get_object().category.user_can_view(self.request.user)

    def handle_no_permission(self):
        messages.error(self.request, _('You don\'t have permission to view that'))
        return redirect('bbs:categories')


class TopicCreate(BaseTopicView, BaseCreateView, SingleObjectMixin):
    form_class = forms.TopicForm

    @property
    def success_url(self):
        return reverse_lazy('bbs:topic-view', kwargs={'pk': self.object.pk})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        # Form will not allow a user to create a topic in a category they dont have access to
        res = super().form_valid(form)
        messages.success(self.request, _('Successfully created a new topic.'))
        return res

    def handle_no_permission(self):
        messages.error(self.request, _('You don\'t have permission create a topic.'))
        return super().handle_no_permission()


class TopicUpdate(BaseTopicView, BaseUpdateView, SingleObjectMixin):
    form_class = forms.TopicForm


class BasePostView(BaseBbsView):
    model = models.Post


class PostCreate(BasePostView, BaseCreateView, SingleObjectMixin):
    form_class = forms.PostForm

    @property
    def success_url(self):
        return reverse_lazy('bbs:topic-view', kwargs={'pk': self.object.topic_id})

    @property
    def topic_id(self):
        return self.request.resolver_match.kwargs.get('topic_id')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.topic_id = self.request.resolver_match.kwargs.get('topic_id')
        res = super().form_valid(form)
        messages.success(self.request, _('Replied successfully.'))
        return res

    def test_func(self):
        if self.request.method == 'POST':
            category = models.Topic.objects.get(pk=self.topic_id).category
            return category.user_can_reply(self.request.user)
        return True

    def handle_no_permission(self):
        messages.error(self.request, _('You don\'t have permission reply to that topic.'))
        return redirect(reverse_lazy('bbs:topic-view', kwargs={'pk': self.topic_id}))


class PostUpdate(BasePostView, BaseUpdateView, SingleObjectMixin):
    form_class = forms.PostForm
