# Generated by Django 3.0.4 on 2020-04-01 09:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('register', '0003_operator_opeartor'),
    ]

    operations = [
        migrations.RenameField(
            model_name='operator',
            old_name='opeartor',
            new_name='operator',
        ),
    ]
