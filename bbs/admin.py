from django.contrib import admin
from . import models


class CategoryAdmin(admin.ModelAdmin):
    filter_horizontal = ('can_create', 'can_reply', 'can_view')


admin.site.register(models.Category, CategoryAdmin)
admin.site.register(models.Topic)
admin.site.register(models.Post)
