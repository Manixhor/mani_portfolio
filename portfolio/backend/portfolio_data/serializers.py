from rest_framework import serializers
from django.conf import settings

from .models import CertificationItem, ExperienceItem, PortfolioConfig, ProjectItem, SkillItem


DEFAULT_CERTIFICATION_IMAGE_URL = 'https://images.unsplash.com/photo-1434030216411-0b793f4b4173?auto=format&fit=crop&w=900&q=80'


class PortfolioConfigSerializer(serializers.ModelSerializer):
    experience = serializers.SerializerMethodField()
    skills = serializers.SerializerMethodField()
    certifications = serializers.SerializerMethodField()
    projects = serializers.SerializerMethodField()

    class Meta:
        model = PortfolioConfig
        fields = ['hero', 'about', 'experience', 'skills', 'certifications', 'projects', 'contact', 'footer', 'updated_at']

    def get_experience(self, obj):
        experience = dict(obj.experience or {})
        items = list(ExperienceItem.objects.filter(is_visible=True))
        if items:
            experience['items'] = [
                {
                    'period': item.period,
                    'role': item.role,
                    'company': item.company,
                    'points': item.point_list(),
                }
                for item in items
            ]
        return experience

    def get_skills(self, obj):
        skills = dict(obj.skills or {})
        items = list(SkillItem.objects.filter(is_visible=True))
        if items:
            skills['items'] = [
                {
                    'name': item.name,
                    'icon': item.icon,
                }
                for item in items
            ]
        return skills

    def get_certifications(self, obj):
        certifications = {
            'sectionLabel': 'Certifications',
            'heading': 'Certifications',
            'items': [],
        }
        items = list(CertificationItem.objects.filter(is_visible=True))
        if items:
            certifications['items'] = [
                {
                    'title': item.title,
                    'issuer': item.issuer,
                    'issuedDate': item.issued_date,
                    'credentialUrl': item.credential_url,
                    'description': item.description,
                    'imageUrl': self.certification_image_url(item),
                    'imageAlt': item.image_alt or f'{item.title} certificate preview',
                }
                for item in items
            ]
        return certifications

    def absolute_file_url(self, file_field):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(file_field.url)
        return f'{settings.PUBLIC_BACKEND_URL}{file_field.url}'

    def certification_image_url(self, item):
        if item.image:
            return self.absolute_file_url(item.image)
        return item.image_url or DEFAULT_CERTIFICATION_IMAGE_URL

    def get_projects(self, obj):
        projects = dict(obj.projects or {})
        items = list(ProjectItem.objects.filter(is_visible=True))
        if items:
            projects['items'] = [
                {
                    'name': item.name,
                    'description': item.description,
                    'brief': item.brief,
                    'stack': item.stack,
                    'liveUrl': item.live_url if item.show_live_url else '',
                    'githubUrl': item.github_url if item.show_github_url else '',
                    'imageUrl': self.project_image_url(item),
                    'imageAlt': item.image_alt,
                }
                for item in items
            ]
        return projects

    def project_image_url(self, item):
        if item.image:
            return self.absolute_file_url(item.image)
        return item.image_url
