# Generated by Django 2.2.7 on 2019-12-01 01:03

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Squirrel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('latitude', models.FloatField(help_text='Latitude')),
                ('longitude', models.FloatField(help_text='Longitude')),
                ('squirrel_id', models.CharField(help_text='Unique Squirrel ID', max_length=50)),
                ('shift', models.CharField(choices=[('AM', 'AM'), ('PM', 'PM')], default='AM', help_text='Shift', max_length=2)),
                ('date', models.DateField(help_text='Date')),
                ('age', models.CharField(choices=[('Adult', 'Adult'), ('Juvenile', 'Juvenile'), ('unknown', 'unknown')], default='unknown', help_text='Age', max_length=16)),
                ('color', models.CharField(choices=[('Gray', 'Gray'), ('Cinnamon', 'Cinnamon'), ('Black', 'Black'), ('unknown', 'unknown')], default='unknown', help_text='Primary Fur Color', max_length=50)),
                ('location', models.CharField(choices=[('Ground Plane', 'Ground Plane'), ('Above Ground', 'Above Ground'), ('unknown', 'unknown')], default='unknown', help_text='Location', max_length=50)),
                ('specific_location', models.CharField(help_text='Specific Location', max_length=100)),
                ('running', models.BooleanField(default=False, help_text='Running')),
                ('chasing', models.BooleanField(default=False, help_text='Chasing')),
                ('climbing', models.BooleanField(default=False, help_text='Climbing')),
                ('eating', models.BooleanField(default=False, help_text='Eating')),
                ('foraging', models.BooleanField(default=False, help_text='Foraging')),
                ('other_activities', models.CharField(help_text='Other Activities', max_length=100)),
                ('kuks', models.BooleanField(default=False, help_text='Kuks')),
                ('quaas', models.BooleanField(default=False, help_text='Quaas')),
                ('moans', models.BooleanField(default=False, help_text='Moans')),
                ('tail_flags', models.BooleanField(default=False, help_text='Tail Flags')),
                ('tail_twitches', models.BooleanField(default=False, help_text='Tail Twitches')),
                ('approaches', models.BooleanField(default=False, help_text='Approaches')),
                ('indifferent', models.BooleanField(default=False, help_text='Indifferent')),
                ('runs_from', models.BooleanField(default=False, help_text='Runs From')),
            ],
        ),
    ]
