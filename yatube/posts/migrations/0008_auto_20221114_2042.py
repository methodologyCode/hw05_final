# Generated by Django 2.2.16 on 2022-11-14 15:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0007_comment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='text',
            field=models.TextField(help_text='Введите текст', verbose_name='Содержание'),
        ),
        migrations.AlterField(
            model_name='post',
            name='text',
            field=models.TextField(help_text='Введите текст', verbose_name='Содержание'),
        ),
    ]
