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
