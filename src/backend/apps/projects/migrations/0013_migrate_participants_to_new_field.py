# Generated by Badmajor on 2024-07-06 18:52

from django.db import migrations


def migrate_participants(apps, scheme_editor):
    Project = apps.get_model('projects', 'Project')
    ProjectParticipant = apps.get_model('projects', 'ProjectParticipant')

    for project in Project.objects.all():
        for participant in project.participants.all():
            specialist = participant.profile.professions.first()
            if specialist:
                profession = specialist.profession
                skills = specialist.skills.all()
            else:
                Profession = apps.get_model('general', 'Profession')
                Skill = apps.get_model('general', 'Skill')
                profession = Profession.objects.first()
                skills = Skill.objects.first()
            project_participant = ProjectParticipant.objects.create(
                project=project,
                user=participant,
                profession=profession
            )

            project_participant.skills.add(skills)


class Migration(migrations.Migration):
    dependencies = [
        ("projects", "0012_projectparticipant_alter_project_participants_and_more"),
    ]

    operations = [
        migrations.RunPython(migrate_participants),
    ]
