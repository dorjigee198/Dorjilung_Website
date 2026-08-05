from .models import Announcement


def site_announcements(request):
    """
    Makes the homepage-ticker announcements available on every page
    (the bar now lives above the header in base.html, not just on
    the homepage), without every view having to fetch it manually.
    """
    return {"site_announcements": Announcement.objects.visible()}
