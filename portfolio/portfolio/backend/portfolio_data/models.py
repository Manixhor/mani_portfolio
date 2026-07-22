from django.db import models


class PortfolioConfig(models.Model):
    hero = models.JSONField(default=dict)
    about = models.JSONField(default=dict)
    experience = models.JSONField(default=dict)
    skills = models.JSONField(default=dict)
    projects = models.JSONField(default=dict)
    contact = models.JSONField(default=dict)
    footer = models.JSONField(default=dict)
    about_image = models.ImageField(upload_to='portfolio/about/', blank=True, null=True)
    contact_image = models.ImageField(upload_to='portfolio/contact/', blank=True, null=True)
    project_1_upload = models.ImageField(upload_to='portfolio/projects/', blank=True, null=True)
    project_2_upload = models.ImageField(upload_to='portfolio/projects/', blank=True, null=True)
    project_3_upload = models.ImageField(upload_to='portfolio/projects/', blank=True, null=True)
    project_4_upload = models.ImageField(upload_to='portfolio/projects/', blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Portfolio Content"
        verbose_name_plural = "Portfolio Content"

    def __str__(self):
        return "Portfolio Content"


class ExperienceItem(models.Model):
    role = models.CharField(max_length=160)
    company = models.CharField(max_length=180)
    period = models.CharField(max_length=120, blank=True)
    points = models.TextField(
        blank=True,
        help_text='Write one bullet point per line.',
    )
    order = models.PositiveIntegerField(default=0)
    is_visible = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', '-id']
        verbose_name = 'Experience'
        verbose_name_plural = 'Experience'

    def __str__(self):
        return f'{self.role} at {self.company}'

    def point_list(self):
        return [point.strip() for point in self.points.splitlines() if point.strip()]


class SkillItem(models.Model):
    name = models.CharField(max_length=80)
    icon = models.CharField(
        max_length=120,
        blank=True,
        help_text='Optional Devicon class, for example: devicon-python-plain',
    )
    order = models.PositiveIntegerField(default=0)
    is_visible = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Skill'
        verbose_name_plural = 'Skills'

    def __str__(self):
        return self.name


class CertificationItem(models.Model):
    title = models.CharField(max_length=180)
    issuer = models.CharField(max_length=180, blank=True)
    issued_date = models.CharField(max_length=120, blank=True)
    credential_url = models.URLField(blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='portfolio/certifications/', blank=True, null=True)
    image_url = models.URLField(blank=True)
    image_alt = models.CharField(max_length=180, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_visible = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', '-id']
        verbose_name = 'Certification'
        verbose_name_plural = 'Certifications'

    def __str__(self):
        return self.title


class ProjectItem(models.Model):
    name = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    brief = models.TextField(blank=True)
    stack = models.CharField(max_length=240, blank=True)
    live_url = models.URLField(blank=True)
    show_live_url = models.BooleanField(default=True)
    github_url = models.URLField(blank=True)
    show_github_url = models.BooleanField(default=True)
    image = models.ImageField(upload_to='portfolio/projects/', blank=True, null=True)
    image_url = models.URLField(blank=True)
    image_alt = models.CharField(max_length=180, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_visible = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', '-id']
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'

    def __str__(self):
        return self.name
