# Generated by Django 5.0.6 on 2024-06-22 10:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0004_alter_tasks_task_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tasks',
            name='task_description',
            field=models.TextField(default='Task description here.....'),
        ),
    ]
