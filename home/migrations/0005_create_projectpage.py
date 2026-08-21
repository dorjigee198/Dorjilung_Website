from django.db import migrations


def create_project_page(apps, schema_editor):
    # HomePage already has children in production (TenderIndexPage etc.),
    # and historical models from apps.get_model() don't carry Wagtail's
    # Page.add_child() method — so the child is inserted directly using
    # treebeard's own path scheme (steplen=4, zero-padded), the same way
    # 0002_create_homepage.py builds the homepage's own path under Root.
    #
    # The next path segment is computed from the actual children in the
    # tree rather than from homepage.numchild — that field can drift out
    # of sync with reality (observed stale in this project's data, which
    # would otherwise collide with the existing "tenders" child page).
    ContentType = apps.get_model("contenttypes.ContentType")
    HomePage = apps.get_model("home.HomePage")
    Page = apps.get_model("wagtailcore.Page")
    ProjectPage = apps.get_model("home.ProjectPage")

    homepage = HomePage.objects.get(slug="home", depth=2)

    content_type, __ = ContentType.objects.get_or_create(
        app_label="home", model="projectpage"
    )

    child_depth = homepage.depth + 1
    existing_children = Page.objects.filter(
        path__startswith=homepage.path, depth=child_depth
    ).count()
    child_path = homepage.path + str(existing_children + 1).zfill(4)

    ProjectPage.objects.create(
        title="Project",
        draft_title="Project",
        slug="project",
        content_type=content_type,
        path=child_path,
        depth=child_depth,
        numchild=0,
        url_path=homepage.url_path + "project/",
        live=True,
        locale_id=homepage.locale_id,
    )

    # Also correct numchild to the real count, so it doesn't cause the
    # same path collision the next time a page is added under Home.
    homepage.numchild = existing_children + 1
    homepage.save()


def remove_project_page(apps, schema_editor):
    ProjectPage = apps.get_model("home.ProjectPage")
    ProjectPage.objects.filter(slug="project").delete()


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0004_projectpage'),
    ]

    operations = [
        migrations.RunPython(create_project_page, remove_project_page),
    ]
