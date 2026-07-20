from django.db import migrations


DEFAULT_GITHUB = "https://github.com/Manixhor"
DEFAULT_LINKEDIN = "https://www.linkedin.com/in/manikanta-gururam/"
PLACEHOLDER_GITHUB = {"", "#", "https://github.com/Mani"}
PLACEHOLDER_LINKEDIN = {"", "#", "https://linkedin.com/in/Mani", "https://www.linkedin.com/in/Mani"}


def set_default_social_links(apps, schema_editor):
    PortfolioConfig = apps.get_model("portfolio_data", "PortfolioConfig")
    for obj in PortfolioConfig.objects.all():
        hero = dict(obj.hero or {})
        social = dict(hero.get("social") or {})
        github = dict(social.get("github") or {})
        linkedin = dict(social.get("linkedin") or {})

        if github.get("url", "") in PLACEHOLDER_GITHUB:
            github["url"] = DEFAULT_GITHUB
            github["label"] = "GitHub"

        if linkedin.get("url", "") in PLACEHOLDER_LINKEDIN:
            linkedin["url"] = DEFAULT_LINKEDIN
            linkedin["label"] = "LinkedIn"

        social["github"] = github
        social["linkedin"] = linkedin
        hero["social"] = social
        obj.hero = hero
        obj.save(update_fields=["hero", "updated_at"])


class Migration(migrations.Migration):

    dependencies = [
        ("portfolio_data", "0007_add_skill_icons"),
    ]

    operations = [
        migrations.RunPython(set_default_social_links, migrations.RunPython.noop),
    ]
