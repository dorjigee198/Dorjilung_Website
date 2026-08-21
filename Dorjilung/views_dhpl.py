from django.shortcuts import render

from careers.models import JobOpening
from cldp.models import CLDPActivity, CLDPSettings, cldp_dashboard_stats
from home.models import Achievement, Milestone
from newsroom.models import GalleryCategory, GalleryImage, NewsItem
from projectmap.models import ProjectLocation
from structure.models import BoardMember, Department, OrganogramSettings
from sustainability.models import EnvironmentSocialDocument
from tenders.models import TenderPage

MEDIA_COVERAGE_LIMIT = 5
PRESS_RELEASE_LIMIT = 5
CLDP_HOME_LIMIT = 4
NOTICE_BOARD_LIMIT = 3
MILESTONE_HOME_LIMIT = 6
ACHIEVEMENT_HOME_LIMIT = 4


def _notice_board_pick(items, count=NOTICE_BOARD_LIMIT):
    """
    Open items first (soonest-closing first), then most-recently-closed
    ones filling any remaining slots — used for the homepage notice
    board, so it leads with whatever's actually actionable.
    """
    open_items = sorted(
        (i for i in items if i.computed_status == "open"),
        key=lambda i: i.closing_date,
    )
    other_items = sorted(
        (i for i in items if i.computed_status != "open"),
        key=lambda i: i.closing_date,
        reverse=True,
    )
    return (open_items + other_items)[:count]

SECTION_BLURBS = {
    'About': "Learn about DHPL's mandate, leadership, and role in Bhutan's hydropower sector.",
    'Project': "Details on the Dorjilung Hydroelectric Power Project — scope, timeline, and technical scale.",
    'Environment & Social': "Our commitment to environmental stewardship, resettlement, and community engagement.",
    'Tenders': "Procurement notices and tender documents will be published here.",
    'Grievance': "Submit a grievance or concern to DHPL for review and response.",
}


def home(request):
    es_documents = EnvironmentSocialDocument.objects.select_related('document')
    board_members = BoardMember.objects.select_related('photo')
    departments = Department.objects.prefetch_related('members__photo')
    org_settings = OrganogramSettings.load(request_or_site=request)

    media_coverage_qs = NewsItem.objects.filter(category='media_coverage')
    press_release_qs = NewsItem.objects.filter(category='press_release')
    total_news_shown = MEDIA_COVERAGE_LIMIT + PRESS_RELEASE_LIMIT
    total_news_count = media_coverage_qs.count() + press_release_qs.count()

    project_locations = ProjectLocation.objects.all()
    project_locations_json = [
        {
            'name': loc.name,
            'type': loc.location_type,
            'lat': loc.latitude,
            'lng': loc.longitude,
            'description': loc.description,
        }
        for loc in project_locations
    ]

    cldp_activities = CLDPActivity.objects.prefetch_related('images__image')
    cldp_settings = CLDPSettings.load(request_or_site=request)

    notice_tenders = _notice_board_pick(list(TenderPage.objects.live()))
    notice_jobs = _notice_board_pick(list(JobOpening.objects.all()))

    milestones = Milestone.objects.all()
    achievements = Achievement.objects.all()

    context = {
        'milestones': milestones,
        'milestones_preview': milestones[:MILESTONE_HOME_LIMIT],
        'achievements': achievements,
        'achievements_preview': achievements[:ACHIEVEMENT_HOME_LIMIT],
        'environment_documents': [d for d in es_documents if d.category == 'environment'],
        'social_documents': [d for d in es_documents if d.category == 'social'],
        'board_members': board_members,
        'departments': departments,
        'org_chart': org_settings.chart_image,
        'media_coverage': media_coverage_qs[:MEDIA_COVERAGE_LIMIT],
        'press_releases': press_release_qs[:PRESS_RELEASE_LIMIT],
        'more_news_count': max(total_news_count - total_news_shown, 0),
        'project_locations': project_locations,
        'project_locations_json': project_locations_json,
        'cldp_intro_text': cldp_settings.intro_text,
        'cldp_activities': cldp_activities[:CLDP_HOME_LIMIT],
        'cldp_more_count': max(cldp_activities.count() - CLDP_HOME_LIMIT, 0),
        'cldp_stats': cldp_dashboard_stats(cldp_activities),
        'notice_tenders': notice_tenders,
        'notice_jobs': notice_jobs,
    }
    return render(request, 'dhpl_home.html', context)


def section_placeholder(request, name):
    return render(request, 'dhpl_section.html', {
        'section_title': name,
        'section_blurb': SECTION_BLURBS.get(name, ''),
    })


def media_centre(request):
    media_coverage = NewsItem.objects.filter(category='media_coverage')
    press_releases = NewsItem.objects.filter(category='press_release')
    categories = GalleryCategory.objects.all()
    gallery_images = GalleryImage.objects.select_related('category', 'image')

    context = {
        'media_coverage': media_coverage,
        'press_releases': press_releases,
        'gallery_categories': categories,
        'gallery_images': gallery_images,
    }
    return render(request, 'dhpl_media.html', context)
