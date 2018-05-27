from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth.models import User, Group


def get_sentinel_user():
    return User.objects.get_or_create(username='deleted')[0]


class CategoryQuerySet(models.QuerySet):
    def visible_for_user(self, user):
        if user.is_superuser:
            return self
        groups = user.groups.values_list('pk', flat=True)
        return self.filter(
            Q(can_create__pk__in=groups) | Q(can_reply__pk__in=groups) | Q(can_view__pk__in=groups)
        )


class CategoryManager(models.Manager):
    def get_queryset(self):
        return CategoryQuerySet(self.model, using=self._db)


class Category(models.Model):
    title = models.CharField(max_length=50)
    can_create = models.ManyToManyField(Group, related_name='category_create', blank=True,
                                        help_text='Can Create topics in this category (implies reply & view)')
    can_reply = models.ManyToManyField(Group, related_name='category_reply', blank=True,
                                       help_text='Can Reply to topics in this category (implies view)')
    can_view = models.ManyToManyField(Group, related_name='category_view', blank=True,
                                      help_text='Can View topics in this category')

    def user_can_create(self, user):
        return user.groups.filter(pk__in=self.can_create.values_list('pk', flat=True)).exists() or user.is_superuser

    def user_can_reply(self, user):
        return (user.groups.filter(pk__in=self.can_reply.values_list('pk', flat=True)).exists()
                or self.user_can_create(user))

    def user_can_view(self, user):
        return (user.groups.filter(pk__in=self.can_view.values_list('pk', flat=True)).exists()
                or self.user_can_reply(user))

    objects = CategoryManager()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['title']


class Topic(models.Model):
    title = models.CharField(max_length=50)
    created_date = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.SET(get_sentinel_user))
    views = models.IntegerField(default=0)
    pinned = models.BooleanField(default=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='topics')

    def __str__(self):
        return '{0} - {1}'.format(self.category, self.title)

    class Meta:
        ordering = ['-pinned', '-created_date']


class Post(models.Model):
    content = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.SET(get_sentinel_user))
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='posts')

    def __str__(self):
        return '{0:.20} - {1} - {2:.50}'.format(self.topic.title, self.created_by.profile.main_character, self.content)

    class Meta:
        ordering = ['created_date']
