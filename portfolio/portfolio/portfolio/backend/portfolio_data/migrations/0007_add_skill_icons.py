from django.db import migrations


ICON_MAP = {
    "python": "devicon-python-plain",
    "django": "devicon-django-plain",
    "drf": "text:DRF",
    "django rest framework": "text:DRF",
    "mysql": "devicon-mysql-plain",
    "postgresql": "devicon-postgresql-plain",
    "postgres": "devicon-postgresql-plain",
    "sql": "devicon-mysql-plain",
    "git": "devicon-git-plain",
    "html": "devicon-html5-plain",
    "html5": "devicon-html5-plain",
    "css": "devicon-css3-plain",
    "css3": "devicon-css3-plain",
    "javascript": "devicon-javascript-plain",
    "js": "devicon-javascript-plain",
    "react": "devicon-react-original",
    "fastapi": "devicon-fastapi-plain",
}


def add_skill_icons(apps, schema_editor):
    PortfolioConfig = apps.get_model("portfolio_data", "PortfolioConfig")
    obj = PortfolioConfig.objects.filter(pk=1).first()
    if not obj:
        return

    skills = dict(obj.skills or {})
    items = []
    for skill in skills.get("items", []):
        item = dict(skill)
        name = item.get("name", "").lower()
        item.setdefault("icon", ICON_MAP.get(name, "devicon-code-plain"))
        items.append(item)

    skills["items"] = items
    obj.skills = skills
    obj.save()


class Migration(migrations.Migration):

    dependencies = [
        ("portfolio_data", "0006_portfolioconfig_about_image_and_more"),
    ]

    operations = [
        migrations.RunPython(add_skill_icons, migrations.RunPython.noop),
    ]
