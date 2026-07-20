from django.db import migrations


def add_section_labels(apps, schema_editor):
    PortfolioConfig = apps.get_model("portfolio_data", "PortfolioConfig")
    obj = PortfolioConfig.objects.filter(pk=1).first()
    if not obj:
        return

    experience = dict(obj.experience or {})
    skills = dict(obj.skills or {})
    projects = dict(obj.projects or {})

    experience.setdefault("sectionLabel", "Experience")
    skills.setdefault("sectionLabel", "Skills")
    projects.setdefault("sectionLabel", "Projects")

    obj.experience = experience
    obj.skills = skills
    obj.projects = projects
    obj.save()


class Migration(migrations.Migration):

    dependencies = [
        ("portfolio_data", "0004_normalize_admin_portfolio_content"),
    ]

    operations = [
        migrations.RunPython(add_section_labels, migrations.RunPython.noop),
    ]
