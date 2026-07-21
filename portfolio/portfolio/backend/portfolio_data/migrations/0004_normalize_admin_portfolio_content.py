from django.db import migrations


RESUME_PROJECTS = [
    {
        "name": "SpendWise",
        "description": "Personal finance tracker with salary allocation, budgeting, JWT authentication, and custom admin analytics.",
        "brief": "SpendWise helps users allocate salary, manage budgets, track spending, and view custom analytics. It includes JWT authentication, admin analytics, REST API endpoints, and production deployment support.",
        "stack": "Django | PostgreSQL | DRF | PWA | Render",
        "liveUrl": "#",
        "githubUrl": "#",
        "imageUrl": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=900&q=80",
    },
    {
        "name": "Water Potability Prediction",
        "description": "Machine learning classifier for water quality prediction with preprocessing, model comparison, and evaluation metrics.",
        "brief": "A machine learning project that predicts whether water is potable using preprocessing, missing-value handling, model comparison, and evaluation metrics across multiple classifiers.",
        "stack": "Python | scikit-learn | SVM | Random Forest",
        "liveUrl": "#",
        "githubUrl": "#",
        "imageUrl": "https://images.unsplash.com/photo-1555949963-aa79dcee981c?auto=format&fit=crop&w=900&q=80",
    },
    {
        "name": "PY-Vault Banking System",
        "description": "Object-oriented banking engine supporting account creation, deposits, withdrawals, balance queries, and PIN authentication.",
        "brief": "PY-Vault is an object-oriented banking system supporting account creation, deposits, withdrawals, balance checks, PIN-based authentication, and safe transaction validation.",
        "stack": "Python | OOP | JSON | CLI",
        "liveUrl": "#",
        "githubUrl": "#",
        "imageUrl": "https://images.unsplash.com/photo-1563986768609-322da13575f3?auto=format&fit=crop&w=900&q=80",
    },
    {
        "name": "Reverse Auction System",
        "description": "Bid comparison and winner-selection algorithm with structured error handling and modular processing layers.",
        "brief": "A reverse auction engine that compares bids, selects winners, handles errors clearly, and separates intake, processing, and result layers for easier testing and maintenance.",
        "stack": "Python | OOP | Error Handling",
        "liveUrl": "#",
        "githubUrl": "#",
        "imageUrl": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=900&q=80",
    },
]


def normalize_portfolio_content(apps, schema_editor):
    PortfolioConfig = apps.get_model("portfolio_data", "PortfolioConfig")
    obj, _ = PortfolioConfig.objects.get_or_create(pk=1)

    hero = dict(obj.hero or {})
    hero.setdefault("eyebrow", "Python Developer Portfolio")
    hero.setdefault("title", "Portfolio")
    hero.setdefault("year", "2026")
    hero.setdefault("resumeLabel", "Download resume")

    about = dict(obj.about or {})
    about.setdefault("imageUrl", "https://images.unsplash.com/photo-1515879218367-8466d910aaa4?auto=format&fit=crop&w=1200&q=80")
    about.setdefault("imageAlt", "Laptop showing code on a developer desk")

    projects = dict(obj.projects or {})
    project_names = {project.get("name") for project in projects.get("items", [])}
    legacy_project_names = {"HRMS", "Subhagruha", "Letter Gen"}
    if legacy_project_names.intersection(project_names):
        projects["heading"] = projects.get("heading") or "Projects"
        projects["items"] = RESUME_PROJECTS

    contact = dict(obj.contact or {})
    social_email = ((hero.get("social") or {}).get("email") or {}).get("url", "")
    contact.setdefault("sectionLabel", "Let's connect")
    contact.setdefault("heading", "Build something amazing together.")
    contact.setdefault("subtitle", "I am always open to new opportunities and exciting projects. Let's build something amazing together!")
    contact.setdefault("email", social_email.replace("mailto:", "") or "manigururam06@gmail.com")
    contact.setdefault("location", "India")
    contact.setdefault("imageUrl", "https://images.unsplash.com/photo-1498050108023-c5249f4df085?auto=format&fit=crop&w=1200&q=80")
    contact.setdefault("imageAlt", "Dark developer workspace with code on a monitor")
    contact.setdefault("quote", '"Code is not just what I write, it is how I solve problems."')

    obj.hero = hero
    obj.about = about
    obj.projects = projects
    obj.contact = contact
    obj.save()


class Migration(migrations.Migration):

    dependencies = [
        ("portfolio_data", "0003_seed_portfolio_content"),
    ]

    operations = [
        migrations.RunPython(normalize_portfolio_content, migrations.RunPython.noop),
    ]
