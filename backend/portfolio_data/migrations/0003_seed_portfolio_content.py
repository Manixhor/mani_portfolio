from django.db import migrations


DEFAULT_HERO = {
    "eyebrow": "Python Developer Portfolio",
    "title": "Portfolio",
    "greeting": "Hi, I'm",
    "name": "Mani",
    "tagline": "Python Developer | Django Developer | Backend Developer | Software Engineer",
    "year": "2026",
    "resumeLabel": "Download resume",
    "resumeUrl": "#",
    "social": {
        "github": {"url": "https://github.com/Mani", "label": "GitHub"},
        "linkedin": {"url": "https://linkedin.com/in/Mani", "label": "LinkedIn"},
        "email": {"url": "mailto:manigururam06@gmail.com", "label": "Email"},
    },
}

DEFAULT_ABOUT = {
    "sectionLabel": "About me",
    "heading": "Developer. Thinker. Creator.",
    "paragraphs": [
        "Python and Django backend developer with production experience shipping REST APIs, HRMS modules, and full-stack web applications used by real users.",
        "I work across Django, Django REST Framework, PostgreSQL, MySQL, deployment workflows, and backend systems that need to stay reliable in production.",
    ],
    "imageUrl": "https://images.unsplash.com/photo-1515879218367-8466d910aaa4?auto=format&fit=crop&w=1200&q=80",
    "imageAlt": "Laptop showing code on a developer desk",
}

DEFAULT_EXPERIENCE = {
    "heading": "Experience",
    "items": [
        {
            "period": "December 2025 - Present",
            "role": "Python Developer Intern",
            "company": "Lagran Software Solutions Pvt Ltd",
            "points": [
                "Built 7 production HRMS modules including Attendance, Leave, Reporting, Employee Management, HR Operations, Asset Management, and Background Verification.",
                "Automated leave-approval email workflows with SMTP integration, reducing HR team response time and eliminating manual communication effort.",
                "Developed and deployed the Subhagruha property web application end-to-end with property listings, blog module, SEO enhancements, and contact forms.",
                "Maintained zero-downtime deployments across simultaneous Django projects by managing Gunicorn, environment variables, and backend-frontend integration.",
            ],
        }
    ],
}

DEFAULT_SKILLS = {
    "heading": "Skills",
    "items": [
        {"name": "Python", "icon": "devicon-python-plain"},
        {"name": "Django", "icon": "devicon-django-plain"},
        {"name": "SQL", "icon": "devicon-mysql-plain"},
        {"name": "HTML", "icon": "devicon-html5-plain"},
        {"name": "CSS", "icon": "devicon-css3-plain"},
        {"name": "JavaScript", "icon": "devicon-javascript-plain"},
        {"name": "React", "icon": "devicon-react-original"},
        {"name": "Git", "icon": "devicon-git-plain"},
        {"name": "FastAPI", "icon": "devicon-fastapi-plain"},
    ],
}

DEFAULT_PROJECTS = {
    "heading": "Projects",
    "items": [
        {
            "name": "SpendWise",
            "description": "Personal finance tracker with salary allocation, budgeting, JWT authentication, and custom admin analytics.",
            "brief": "SpendWise is a personal finance tracker that helps users allocate salary, manage budgets, track spending, and view custom analytics. It includes JWT authentication, admin analytics, and production deployment support.",
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
    ],
}

DEFAULT_CONTACT = {
    "sectionLabel": "Let's connect",
    "heading": "Build something amazing together.",
    "subtitle": "I am always open to new opportunities and exciting projects. Let's build something amazing together!",
    "email": "manigururam06@gmail.com",
    "phone": "+91 9912303719",
    "location": "India",
    "imageUrl": "https://images.unsplash.com/photo-1498050108023-c5249f4df085?auto=format&fit=crop&w=1200&q=80",
    "imageAlt": "Dark developer workspace with code on a monitor",
    "quote": '"Code is not just what I write, it\'s how I solve problems."',
}

DEFAULT_FOOTER = {
    "copyright": "(c) 2026 Mani. All rights reserved.",
}


def seed_portfolio_content(apps, schema_editor):
    PortfolioConfig = apps.get_model("portfolio_data", "PortfolioConfig")
    obj, _ = PortfolioConfig.objects.get_or_create(pk=1)
    defaults = {
        "hero": DEFAULT_HERO,
        "about": DEFAULT_ABOUT,
        "experience": DEFAULT_EXPERIENCE,
        "skills": DEFAULT_SKILLS,
        "projects": DEFAULT_PROJECTS,
        "contact": DEFAULT_CONTACT,
        "footer": DEFAULT_FOOTER,
    }
    changed = False
    for field, value in defaults.items():
        if not getattr(obj, field):
            setattr(obj, field, value)
            changed = True
    if changed:
        obj.save()


class Migration(migrations.Migration):

    dependencies = [
        ("portfolio_data", "0002_alter_portfolioconfig_options"),
    ]

    operations = [
        migrations.RunPython(seed_portfolio_content, migrations.RunPython.noop),
    ]
