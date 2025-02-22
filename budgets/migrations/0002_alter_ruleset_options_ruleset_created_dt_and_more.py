# Generated by Django 5.0.6 on 2024-06-30 13:54

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('budgets', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ruleset',
            options={'ordering': ['-created_dt']},
        ),
        migrations.AddField(
            model_name='ruleset',
            name='created_dt',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterUniqueTogether(
            name='ruleset',
            unique_together={('user', 'name')},
        ),
    ]
