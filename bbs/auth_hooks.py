from . import urls
from django.utils.translation import ugettext_lazy as _
from allianceauth import hooks
from allianceauth.services.hooks import MenuItemHook, UrlHook


@hooks.register('menu_item_hook')
def register_menu():
    return MenuItemHook(_('Forum'), 'fa fa-comments fa-fw', 'bbs:categories',
                        navactive=['bbs:'])


@hooks.register('url_hook')
def register_url():
    return UrlHook(urls, 'forum', r'^forum/')


@hooks.register('url_hook')
def register_markdown_url():
    return UrlHook('martor.urls', None, r'^martor/')
