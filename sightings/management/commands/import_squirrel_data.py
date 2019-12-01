from django.core.management.base import BaseCommand, CommandError
from sightings.models import Squirrel
import csv
import datetime

class Command(BaseCommand):
    help = 'import squirrel data from custom path'

    def booler(self, b):
        if b.lower() == "true":
            return True
        else:
            return False

    def add_arguments(self, parser):
        parser.add_argument('path', type=str, help='/path/to/file.csv')

    def handle(self, *args, **options):
        path = options['path']

        with open(path) as f:
            data = csv.reader(f)

            title = True
            for row in data:
                if title:
                    title = False
                else:
                    if row[4] == 'AM':
                        shift_temp = Squirrel.AM
                    else:
                        shift_temp = Squirrel.PM

                    if row[7] == 'Adult':
                        age_temp = Squirrel.ADULT
                    elif row[7] == 'Juvenile':
                        age_temp = Squirrel.JUVENILE
                    else:
                        age_temp = Squirrel.UNKNOWN

                    if row[8] == 'Gray':
                        color_temp = Squirrel.GRAY
                    elif row[8] == 'Cinnamon':
                        color_temp = Squirrel.CINNAMON
                    elif row[8] == 'Black':
                        color_temp = Squirrel.BLACK
                    else:
                        color_temp = Squirrel.UNKNOWN

                    if row[12] == 'Ground Plane':
                        location_temp = Squirrel.GROUND_PLANE
                    elif row[12] == 'Above Ground':
                        location_temp = Squirrel.ABOVE_GROUND
                    else:
                        location_temp = Squirrel.UNKNOWN

                    _, created = Squirrel.objects.get_or_create(
                        latitude = float(row[0]),
                        longitude = float(row[1]),
                        squirrel_id = row[2],
                        shift = shift_temp,
                        date = datetime.date(int(row[5][-4:]),int(row[5][:2]),int(row[5][2:4])),
                        age = age_temp,
                        color = color_temp,
                        location = location_temp,
                        specific_location = row[14],
                        running = self.booler(row[15]),
                        chasing = self.booler(row[16]),
                        climbing = self.booler(row[17]),
                        eating = self.booler(row[18]),
                        foraging = self.booler(row[19]),
                        other_activities = row[20],
                        kuks = self.booler(row[21]),
                        quaas = self.booler(row[22]),
                        moans = self.booler(row[23]),
                        tail_flags = self.booler(row[24]),
                        tail_twitches = self.booler(row[25]),
                        approaches = self.booler(row[26]),
                        indifferent = self.booler(row[27]),
                        runs_from = self.booler(row[28]),
                    )


        self.stdout.write(self.style.SUCCESS(f'Successfully imported squirrel data from {path}'))
