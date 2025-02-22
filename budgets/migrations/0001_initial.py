# Generated by Django 5.0.6 on 2024-06-30 13:31

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='', max_length=50, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Budget',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=50)),
                ('created_dt', models.DateTimeField(auto_now=True)),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='budget', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_dt'],
                'unique_together': {('user', 'name')},
            },
        ),
        migrations.CreateModel(
            name='BudgetCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('limit', models.DecimalField(decimal_places=2, max_digits=7)),
                ('budget', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='budget_category', to='budgets.budget')),
                ('category', models.ForeignKey(default='', on_delete=django.db.models.deletion.DO_NOTHING, to='budgets.category')),
            ],
        ),
        migrations.CreateModel(
            name='Ruleset',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=50)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ruleset', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Rule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('keyword', models.CharField(max_length=100)),
                ('category', models.ForeignKey(default='', on_delete=django.db.models.deletion.DO_NOTHING, to='budgets.category')),
                ('ruleset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rule', to='budgets.ruleset')),
            ],
        ),
    ]
