# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Mqq',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('alias', models.CharField(max_length=20)),
                ('type', models.CharField(max_length=3)),
                ('env', models.CharField(max_length=20)),
                ('deep', models.IntegerField()),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='mqq',
            unique_together=set([('alias', 'env')]),
        ),
    ]
