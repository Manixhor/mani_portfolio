import json

from django.contrib import admin
from django import forms
from django.conf import settings
from django.utils.html import format_html, format_html_join
from tinymce.widgets import TinyMCE
from .models import PortfolioConfig


class PrettyJSONTextarea(forms.Textarea):
    def format_value(self, value):
        if value in (None, ''):
            return ''

        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                return value

        return json.dumps(value, indent=2, ensure_ascii=False)


class PortfolioConfigForm(forms.ModelForm):
    hero_title = forms.CharField(label='Hero Large Title', required=False)
    hero_greeting = forms.CharField(
        label='Greeting',
        required=False,
        help_text='Example: Hi, I am',
    )
    hero_name = forms.CharField(
        label='Name',
        required=False,
        help_text='Shown in the portfolio hero section.',
    )
    hero_tagline = forms.CharField(
        label='Hero Tagline',
        required=False,
        help_text='Short role summary below the name.',
    )
    hero_year = forms.CharField(label='Hero Year Button', required=False)
    resume_url = forms.URLField(
        label='Resume URL',
        required=False,
        help_text='Paste a public resume PDF link.',
    )
    github_url = forms.URLField(
        label='GitHub URL',
        required=False,
    )
    linkedin_url = forms.URLField(
        label='LinkedIn URL',
        required=False,
    )
    hero_email = forms.EmailField(
        label='Hero Email',
        required=False,
    )
    about_heading = forms.CharField(
        label='About Heading',
        required=False,
    )
    about_section_label = forms.CharField(
        label='About Small Label',
        required=False,
    )
    about_html = forms.CharField(
        label='About Text',
        widget=TinyMCE(attrs={'cols': 80, 'rows': 14}),
        required=False,
        help_text='Use rich text here. Each paragraph is saved back into the about JSON.',
    )
    about_image_url = forms.URLField(label='About Image URL', required=False)
    about_image_alt = forms.CharField(label='About Image Alt Text', required=False)
    experience_section_label = forms.CharField(label='Experience Small Label', required=False)
    experience_heading = forms.CharField(label='Experience Heading', required=False)
    experience_period = forms.CharField(label='Experience Period', required=False)
    experience_role = forms.CharField(label='Experience Role', required=False)
    experience_company = forms.CharField(label='Experience Company', required=False)
    experience_points = forms.CharField(
        label='Experience Bullet Points',
        widget=forms.Textarea(attrs={'rows': 7}),
        required=False,
        help_text='Write one bullet point per line.',
    )
    skills_list = forms.CharField(
        label='Skills',
        widget=forms.Textarea(attrs={'rows': 4}),
        required=False,
        help_text='Comma-separated skills, for example: Python, Django, SQL, HTML, CSS',
    )
    skills_section_label = forms.CharField(label='Skills Small Label', required=False)
    skills_heading = forms.CharField(label='Skills Heading', required=False)
    projects_section_label = forms.CharField(label='Projects Small Label', required=False)
    projects_heading = forms.CharField(label='Projects Heading', required=False)
    project_1_name = forms.CharField(label='Project 1 Name', required=False)
    project_1_description = forms.CharField(label='Project 1 Short Description', widget=forms.Textarea(attrs={'rows': 3}), required=False)
    project_1_brief = forms.CharField(label='Project 1 Brief', widget=forms.Textarea(attrs={'rows': 4}), required=False)
    project_1_stack = forms.CharField(label='Project 1 Stack', required=False)
    project_1_live = forms.URLField(label='Project 1 Live Link', required=False)
    project_1_github = forms.URLField(label='Project 1 GitHub Link', required=False)
    project_1_image = forms.URLField(label='Project 1 Image URL', required=False)
    project_2_name = forms.CharField(label='Project 2 Name', required=False)
    project_2_description = forms.CharField(label='Project 2 Short Description', widget=forms.Textarea(attrs={'rows': 3}), required=False)
    project_2_brief = forms.CharField(label='Project 2 Brief', widget=forms.Textarea(attrs={'rows': 4}), required=False)
    project_2_stack = forms.CharField(label='Project 2 Stack', required=False)
    project_2_live = forms.URLField(label='Project 2 Live Link', required=False)
    project_2_github = forms.URLField(label='Project 2 GitHub Link', required=False)
    project_2_image = forms.URLField(label='Project 2 Image URL', required=False)
    project_3_name = forms.CharField(label='Project 3 Name', required=False)
    project_3_description = forms.CharField(label='Project 3 Short Description', widget=forms.Textarea(attrs={'rows': 3}), required=False)
    project_3_brief = forms.CharField(label='Project 3 Brief', widget=forms.Textarea(attrs={'rows': 4}), required=False)
    project_3_stack = forms.CharField(label='Project 3 Stack', required=False)
    project_3_live = forms.URLField(label='Project 3 Live Link', required=False)
    project_3_github = forms.URLField(label='Project 3 GitHub Link', required=False)
    project_3_image = forms.URLField(label='Project 3 Image URL', required=False)
    project_4_name = forms.CharField(label='Project 4 Name', required=False)
    project_4_description = forms.CharField(label='Project 4 Short Description', widget=forms.Textarea(attrs={'rows': 3}), required=False)
    project_4_brief = forms.CharField(label='Project 4 Brief', widget=forms.Textarea(attrs={'rows': 4}), required=False)
    project_4_stack = forms.CharField(label='Project 4 Stack', required=False)
    project_4_live = forms.URLField(label='Project 4 Live Link', required=False)
    project_4_github = forms.URLField(label='Project 4 GitHub Link', required=False)
    project_4_image = forms.URLField(label='Project 4 Image URL', required=False)
    contact_email = forms.EmailField(
        label='Contact Email',
        required=False,
    )
    contact_phone = forms.CharField(
        label='Contact Phone',
        required=False,
    )
    contact_location = forms.CharField(
        label='Contact Location',
        required=False,
    )
    contact_heading = forms.CharField(
        label='Contact Heading',
        required=False,
    )
    contact_section_label = forms.CharField(
        label='Contact Small Label',
        required=False,
    )
    contact_subtitle = forms.CharField(
        label='Contact Subtitle',
        widget=TinyMCE(attrs={'cols': 80, 'rows': 8}),
        required=False,
    )
    contact_image_url = forms.URLField(label='Contact Image URL', required=False)
    contact_image_alt = forms.CharField(label='Contact Image Alt Text', required=False)
    contact_quote = forms.CharField(label='Contact Quote', widget=forms.Textarea(attrs={'rows': 3}), required=False)

    class Meta:
        model = PortfolioConfig
        fields = '__all__'
        help_texts = {
            'hero': 'Hero content, resume URL, and social links.',
            'about': 'About heading, rich text paragraphs, and summary details.',
            'experience': 'Work history entries and bullet points.',
            'skills': 'Skill names, percentages, or displayed tech stack.',
            'projects': 'Project cards, briefs, live links, and GitHub links.',
            'contact': 'Contact heading, subtitle, form/API details, email, and phone.',
            'footer': 'Footer copyright and social/footer links.',
        }
        widgets = {
            'hero': PrettyJSONTextarea(attrs={'rows': 16, 'class': 'vLargeTextField json-editor', 'spellcheck': 'false'}),
            'about': PrettyJSONTextarea(attrs={'rows': 16, 'class': 'vLargeTextField json-editor', 'spellcheck': 'false'}),
            'experience': PrettyJSONTextarea(attrs={'rows': 16, 'class': 'vLargeTextField json-editor', 'spellcheck': 'false'}),
            'skills': PrettyJSONTextarea(attrs={'rows': 12, 'class': 'vLargeTextField json-editor', 'spellcheck': 'false'}),
            'projects': PrettyJSONTextarea(attrs={'rows': 18, 'class': 'vLargeTextField json-editor', 'spellcheck': 'false'}),
            'contact': PrettyJSONTextarea(attrs={'rows': 12, 'class': 'vLargeTextField json-editor', 'spellcheck': 'false'}),
            'footer': PrettyJSONTextarea(attrs={'rows': 12, 'class': 'vLargeTextField json-editor', 'spellcheck': 'false'}),
        }

    @staticmethod
    def file_url(file_field):
        if file_field:
            return f'{settings.PUBLIC_BACKEND_URL}{file_field.url}'
        return ''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        hero = self.instance.hero or {}
        about = self.instance.about or {}
        experience = self.instance.experience or {}
        skills = self.instance.skills or {}
        projects = self.instance.projects or {}
        contact = self.instance.contact or {}
        social = hero.get('social', {})
        github = social.get('github', {})
        linkedin = social.get('linkedin', {})
        email = social.get('email', {})

        self.fields['hero_title'].initial = hero.get('title', '')
        self.fields['hero_greeting'].initial = hero.get('greeting', '')
        self.fields['hero_name'].initial = hero.get('name', '')
        self.fields['hero_tagline'].initial = hero.get('tagline', '')
        self.fields['hero_year'].initial = hero.get('year', '')
        self.fields['resume_url'].initial = '' if hero.get('resumeUrl') == '#' else hero.get('resumeUrl', '')
        self.fields['github_url'].initial = '' if github.get('url') == '#' else github.get('url', '')
        self.fields['linkedin_url'].initial = '' if linkedin.get('url') == '#' else linkedin.get('url', '')
        self.fields['hero_email'].initial = email.get('url', '').replace('mailto:', '')
        self.fields['about_image'].label = 'About Image Upload'
        self.fields['about_image'].help_text = 'Upload an image from your computer. This is used before the URL below.'
        self.fields['contact_image'].label = 'Contact Image Upload'
        self.fields['contact_image'].help_text = 'Upload an image from your computer. This is used before the URL below.'
        for index in range(1, 5):
            self.fields[f'project_{index}_upload'].label = f'Project {index} Image Upload'
            self.fields[f'project_{index}_upload'].help_text = 'Upload a project screenshot. This is used before the URL below.'
        self.fields['about_section_label'].initial = about.get('sectionLabel', '')
        self.fields['about_heading'].initial = about.get('heading', '')
        about_paragraphs = []
        for paragraph in about.get('paragraphs', []):
            if '<' in paragraph and '>' in paragraph:
                about_paragraphs.append(paragraph)
            else:
                about_paragraphs.append(f'<p>{paragraph}</p>')
        self.fields['about_html'].initial = ''.join(about_paragraphs)
        self.fields['about_image_url'].initial = about.get('imageUrl', '')
        self.fields['about_image_alt'].initial = about.get('imageAlt', '')
        self.fields['experience_section_label'].initial = experience.get('sectionLabel', '')
        self.fields['experience_heading'].initial = experience.get('heading', '')
        experience_items = experience.get('items', [])
        if experience_items:
            item = experience_items[0]
            self.fields['experience_period'].initial = item.get('period', '')
            self.fields['experience_role'].initial = item.get('role', '')
            self.fields['experience_company'].initial = item.get('company', '')
            self.fields['experience_points'].initial = '\n'.join(item.get('points', []))
        self.fields['skills_section_label'].initial = skills.get('sectionLabel', '')
        self.fields['skills_heading'].initial = skills.get('heading', '')
        self.fields['skills_list'].initial = ', '.join(skill.get('name', '') for skill in skills.get('items', []))
        self.fields['projects_section_label'].initial = projects.get('sectionLabel', '')
        self.fields['projects_heading'].initial = projects.get('heading', '')
        for index, project in enumerate(projects.get('items', [])[:4], start=1):
            self.fields[f'project_{index}_name'].initial = project.get('name', '')
            self.fields[f'project_{index}_description'].initial = project.get('description', '')
            self.fields[f'project_{index}_brief'].initial = project.get('brief', '')
            self.fields[f'project_{index}_stack'].initial = project.get('stack') or ' | '.join(project.get('tags', []))
            self.fields[f'project_{index}_live'].initial = '' if project.get('liveUrl') == '#' else project.get('liveUrl', '')
            self.fields[f'project_{index}_github'].initial = '' if project.get('githubUrl') == '#' else project.get('githubUrl', '')
            self.fields[f'project_{index}_image'].initial = project.get('imageUrl', '')
        self.fields['contact_email'].initial = contact.get('email', '') or email.get('url', '').replace('mailto:', '')
        self.fields['contact_phone'].initial = contact.get('phone', '')
        self.fields['contact_location'].initial = contact.get('location', '')
        self.fields['contact_section_label'].initial = contact.get('sectionLabel', '')
        self.fields['contact_heading'].initial = contact.get('heading', '')
        self.fields['contact_subtitle'].initial = contact.get('subtitle', '')
        self.fields['contact_image_url'].initial = contact.get('imageUrl', '')
        self.fields['contact_image_alt'].initial = contact.get('imageAlt', '')
        self.fields['contact_quote'].initial = contact.get('quote', '')
        for field_name in ['hero', 'about', 'experience', 'skills', 'projects', 'contact', 'footer']:
            value = getattr(self.instance, field_name, None)
            if value:
                self.initial[field_name] = json.dumps(value, indent=2, ensure_ascii=False)

    def save(self, commit=True):
        instance = super().save(commit=False)

        hero = dict(instance.hero or {})
        about = dict(instance.about or {})
        experience = dict(instance.experience or {})
        skills = dict(instance.skills or {})
        projects = dict(instance.projects or {})
        contact = dict(instance.contact or {})
        social = dict(hero.get('social', {}))

        hero['title'] = self.cleaned_data.get('hero_title') or hero.get('title', '')
        hero['greeting'] = self.cleaned_data.get('hero_greeting') or hero.get('greeting', '')
        hero['name'] = self.cleaned_data.get('hero_name') or hero.get('name', '')
        hero['tagline'] = self.cleaned_data.get('hero_tagline') or hero.get('tagline', '')
        hero['year'] = self.cleaned_data.get('hero_year') or hero.get('year', '')
        hero['resumeUrl'] = self.cleaned_data.get('resume_url') or hero.get('resumeUrl', '#')

        about['sectionLabel'] = self.cleaned_data.get('about_section_label') or about.get('sectionLabel', '')
        about['heading'] = self.cleaned_data.get('about_heading') or about.get('heading', '')
        about_html = self.cleaned_data.get('about_html')
        if about_html:
            about['paragraphs'] = [about_html]
        about['imageUrl'] = self.file_url(instance.about_image) or self.cleaned_data.get('about_image_url') or about.get('imageUrl', '')
        about['imageAlt'] = self.cleaned_data.get('about_image_alt') or about.get('imageAlt', '')

        experience['sectionLabel'] = self.cleaned_data.get('experience_section_label') or experience.get('sectionLabel', '')
        experience['heading'] = self.cleaned_data.get('experience_heading') or experience.get('heading', '')
        experience['items'] = [{
            'period': self.cleaned_data.get('experience_period') or '',
            'role': self.cleaned_data.get('experience_role') or '',
            'company': self.cleaned_data.get('experience_company') or '',
            'points': [
                point.strip()
                for point in (self.cleaned_data.get('experience_points') or '').splitlines()
                if point.strip()
            ],
        }]

        icon_map = {
            'python': 'devicon-python-plain',
            'django': 'devicon-django-plain',
            'drf': 'text:DRF',
            'django rest framework': 'text:DRF',
            'sql': 'devicon-mysql-plain',
            'mysql': 'devicon-mysql-plain',
            'postgresql': 'devicon-postgresql-plain',
            'html': 'devicon-html5-plain',
            'css': 'devicon-css3-plain',
            'javascript': 'devicon-javascript-plain',
            'react': 'devicon-react-original',
            'git': 'devicon-git-plain',
            'fastapi': 'devicon-fastapi-plain',
        }
        skill_names = [
            skill.strip()
            for skill in (self.cleaned_data.get('skills_list') or '').split(',')
            if skill.strip()
        ]
        skills['sectionLabel'] = self.cleaned_data.get('skills_section_label') or skills.get('sectionLabel', '')
        skills['heading'] = self.cleaned_data.get('skills_heading') or skills.get('heading', '')
        skills['items'] = [
            {'name': name, 'icon': icon_map.get(name.lower(), 'devicon-code-plain')}
            for name in skill_names
        ]

        project_items = []
        for index in range(1, 5):
            name = self.cleaned_data.get(f'project_{index}_name')
            if not name:
                continue
            project_items.append({
                'name': name,
                'description': self.cleaned_data.get(f'project_{index}_description') or '',
                'brief': self.cleaned_data.get(f'project_{index}_brief') or '',
                'stack': self.cleaned_data.get(f'project_{index}_stack') or '',
                'liveUrl': self.cleaned_data.get(f'project_{index}_live') or '#',
                'githubUrl': self.cleaned_data.get(f'project_{index}_github') or '#',
                'imageUrl': self.file_url(getattr(instance, f'project_{index}_upload')) or self.cleaned_data.get(f'project_{index}_image') or '',
            })
        projects['sectionLabel'] = self.cleaned_data.get('projects_section_label') or projects.get('sectionLabel', '')
        projects['heading'] = self.cleaned_data.get('projects_heading') or projects.get('heading', '')
        projects['items'] = project_items

        contact['sectionLabel'] = self.cleaned_data.get('contact_section_label') or contact.get('sectionLabel', '')
        contact['heading'] = self.cleaned_data.get('contact_heading') or contact.get('heading', '')
        contact['subtitle'] = self.cleaned_data.get('contact_subtitle') or contact.get('subtitle', '')
        contact['email'] = self.cleaned_data.get('contact_email') or contact.get('email', '')
        contact['phone'] = self.cleaned_data.get('contact_phone') or contact.get('phone', '')
        contact['location'] = self.cleaned_data.get('contact_location') or contact.get('location', '')
        contact['imageUrl'] = self.file_url(instance.contact_image) or self.cleaned_data.get('contact_image_url') or contact.get('imageUrl', '')
        contact['imageAlt'] = self.cleaned_data.get('contact_image_alt') or contact.get('imageAlt', '')
        contact['quote'] = self.cleaned_data.get('contact_quote') or contact.get('quote', '')

        github_url = self.cleaned_data.get('github_url')
        if github_url:
            social['github'] = {
                'url': github_url,
                'label': 'GitHub',
            }

        linkedin_url = self.cleaned_data.get('linkedin_url')
        if linkedin_url:
            social['linkedin'] = {
                'url': linkedin_url,
                'label': 'LinkedIn',
            }

        hero_email = self.cleaned_data.get('hero_email')
        if hero_email:
            social['email'] = {
                'url': f'mailto:{hero_email}',
                'label': 'Email',
            }

        email_address = self.cleaned_data.get('contact_email')
        if email_address:
            social['email'] = {
                'url': f'mailto:{email_address}',
                'label': 'Email',
            }

        hero['social'] = social

        instance.hero = hero
        instance.about = about
        instance.experience = experience
        instance.skills = skills
        instance.projects = projects
        instance.contact = contact

        if commit:
            instance.save()
        return instance

    class Media:
        css = {'all': ('admin/css/custom_admin.css',)}


@admin.register(PortfolioConfig)
class PortfolioConfigAdmin(admin.ModelAdmin):
    form = PortfolioConfigForm
    list_display = ['id', 'hero_name_display', 'project_count', 'updated_at']
    readonly_fields = [
        'updated_at',
    ]
    fieldsets = [
        ('1. Hero', {
            'fields': [
                'hero_title',
                'hero_greeting',
                'hero_name',
                'hero_tagline',
                'hero_year',
                'resume_url',
                'github_url',
                'linkedin_url',
                'hero_email',
            ],
            'description': 'Top section of the portfolio.',
        }),
        ('2. About', {
            'fields': [
                'about_section_label',
                'about_heading',
                'about_html',
                'about_image',
                'about_image_url',
                'about_image_alt',
            ],
        }),
        ('3. Experience', {
            'fields': [
                'experience_section_label',
                'experience_heading',
                'experience_period',
                'experience_role',
                'experience_company',
                'experience_points',
            ],
        }),
        ('4. Skills', {
            'fields': ['skills_section_label', 'skills_heading', 'skills_list'],
        }),
        ('5. Projects', {
            'fields': [
                'projects_section_label',
                'projects_heading',
                'project_1_name',
                'project_1_description',
                'project_1_brief',
                'project_1_stack',
                'project_1_live',
                'project_1_github',
                'project_1_upload',
                'project_1_image',
                'project_2_name',
                'project_2_description',
                'project_2_brief',
                'project_2_stack',
                'project_2_live',
                'project_2_github',
                'project_2_upload',
                'project_2_image',
                'project_3_name',
                'project_3_description',
                'project_3_brief',
                'project_3_stack',
                'project_3_live',
                'project_3_github',
                'project_3_upload',
                'project_3_image',
                'project_4_name',
                'project_4_description',
                'project_4_brief',
                'project_4_stack',
                'project_4_live',
                'project_4_github',
                'project_4_upload',
                'project_4_image',
            ],
        }),
        ('6. Contact', {
            'fields': [
                'contact_section_label',
                'contact_heading',
                'contact_subtitle',
                'contact_email',
                'contact_phone',
                'contact_location',
                'contact_image',
                'contact_image_url',
                'contact_image_alt',
                'contact_quote',
            ],
        }),
        ('Metadata', {'fields': ['updated_at']}),
    ]

    def has_add_permission(self, request):
        return not PortfolioConfig.objects.exists()

    @admin.display(description='Name')
    def hero_name_display(self, obj):
        return (obj.hero or {}).get('name', 'Portfolio')

    @admin.display(description='Projects')
    def project_count(self, obj):
        return len((obj.projects or {}).get('items', []))

    @admin.display(description='Experience Summary')
    def experience_preview(self, obj):
        items = (obj.experience or {}).get('items', [])
        if not items:
            return format_html('<div class="admin-preview">No experience content yet.</div>')

        rows = format_html_join(
            '',
            '<li><strong>{}</strong> at {} <span>({})</span></li>',
            (
                (
                    item.get('role', 'Role'),
                    item.get('company', 'Company'),
                    item.get('period', 'Period'),
                )
                for item in items
            ),
        )
        return format_html(
            '<div class="admin-preview"><ul>{}</ul></div>',
            rows,
        )

    @admin.display(description='Skills Summary')
    def skills_preview(self, obj):
        skills = (obj.skills or {}).get('items', [])
        if not skills:
            return format_html('<div class="admin-preview">No skills content yet.</div>')

        names = ', '.join(skill.get('name', 'Skill') for skill in skills)
        return format_html('<div class="admin-preview">{}</div>', names)

    @admin.display(description='Projects Summary')
    def projects_preview(self, obj):
        projects = (obj.projects or {}).get('items', [])
        if not projects:
            return format_html('<div class="admin-preview">No project content yet.</div>')

        rows = format_html_join(
            '',
            '<li><strong>{}</strong> - {}</li>',
            (
                (
                    project.get('name', 'Untitled'),
                    project.get('description', 'No description'),
                )
                for project in projects
            ),
        )
        return format_html(
            '<div class="admin-preview"><ul>{}</ul></div>',
            rows,
        )
