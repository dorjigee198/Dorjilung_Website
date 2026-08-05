from django.urls import path, reverse

from wagtail import hooks
from wagtail.admin.menu import MenuItem

from . import views


@hooks.register("register_admin_urls")
def register_gallery_manager_url():
    return [
        path("gallery-manager/", views.gallery_manager, name="newsroom_gallery_manager"),
    ]


@hooks.register("register_admin_menu_item")
def register_gallery_manager_menu_item():
    return MenuItem(
        "Gallery Bulk Manager",
        reverse("newsroom_gallery_manager"),
        icon_name="image",
        order=9000,
    )
