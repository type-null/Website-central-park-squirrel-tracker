from django.core.management.base import BaseCommand, CommandError
from sightings.models import Squirrel
import csv
import datetime

class Command(BaseCommand):
    help = 'import squirrel data from custom path'

    def booler(b):
        if b.lower() == "true":
            return True
        else:
            return False

    def add_arguments(self, parser):
        parser.add_argument('path', nargs='+', type=str, help='/path/to/file.csv')

    def handle(self, *args, **options):
        path = options['path']

        with open(path) as f:
            data = csv.reader(f)

            title = True
            for row in data:
                if title:
                    title = False
                else:

                    if row[7] is in ['Adult', 'Juvenile']:
                        age_temp = row[7]
                    else:
                        age_temp = 'Other'

                    if row[8] is in ['Gray', 'Cinnamon','Black']:
                        color_temp = row[8]
                    else:
                        color_temp = 'Unknown'

                    if row[12] is in ['Ground Plane', 'Above Ground']:
                        location_temp = row[12]
                    else:
                        location_temp = 'Unknown'

                    _, created = Squirrel.objects.get_or_create(
                        latitude, longtitude = float(row[0]), float(row[1]),
                        squirrel_id, shift = row[2], row[4],
                        date = datetime.date(int(row[5][-4:]),int(row[5][:2]),int(row[5][2:4])),
                        age = age_temp,
                        color = color_temp,
                        location = location_temp,
                        specific_location = row[14],
                        running = booler(row[15]),
                        chasing = booler(row[16]),
                        climbing = booler(row[17]),
                        eating = booler(row[18]),
                        foraging = booler(row[19]),
                        other_activities = row[20],
                        kuks = booler(row[21]),
                        quaas = booler(row[22]),
                        moans = booler(row[23]),
                        tail_flags = booler(row[24]),
                        tail_twitches = booler(row[25]),
                        approaches = booler(row[26]),
                        indifferent = booler(row[27]),
                        runs_from = booler(row[28]),
                    )


        self.stdout.write(self.style.SUCCESS(f'Successfully imported squirrel data from {path}'))
