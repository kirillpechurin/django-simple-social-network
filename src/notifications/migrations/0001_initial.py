# Generated by Django 5.0.3 on 2024-04-17 15:18

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
            name='NotificationEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='SystemNotificationType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='SystemNotification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField(verbose_name='message')),
                ('is_read', models.BooleanField(default=False, verbose_name='read status')),
                ('payload', models.JSONField(default=dict, verbose_name='payload')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='system_notifications', to='notifications.notificationevent', verbose_name='event')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='system_notifications', to=settings.AUTH_USER_MODEL, verbose_name='user')),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='notifications', to='notifications.systemnotificationtype', verbose_name='type')),
            ],
        ),
    ]
