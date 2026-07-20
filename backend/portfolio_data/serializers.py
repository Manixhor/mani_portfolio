from rest_framework import serializers
from django.conf import settings

from .models import ExperienceItem, PortfolioConfig, ProjectItem, SkillItem


class PortfolioConfigSerializer(serializers.ModelSerializer):
    experience = serializers.SerializerMethodField()
    skills = serializers.SerializerMethodField()
    projects = serializers.SerializerMethodField()

    class Meta:
        model = PortfolioConfig
        fields = ['hero', 'about', 'experience', 'skills', 'projects', 'contact', 'footer', 'updated_at']

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

    @staticmethod
    def project_image_url(item):
        if item.image:
            return f'{settings.PUBLIC_BACKEND_URL}{item.image.url}'
        return item.image_url
