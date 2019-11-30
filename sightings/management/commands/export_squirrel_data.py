from django.core.management.base import BaseCommand, CommandError
from sightings.models import Squirrel
import datetime
import pandas as pd

class Command(BaseCommand):
    
    help = 'export squirrel data to custom path'
    
    def add_arguments(self, parser):
        parser.add_argument('path', nargs='+', type=str, help='/path/to/file.csv')
        
    def handle(self, *args, **options):
        path = options['path']
        df = pd.DataFrame(Squirrel.objects.all().values())
        df['date'] = pd.to_datetime(df['date'])
        df.to_csv(path)
        
        self.stdout.write(self.style.SUCCESS(f'Successfully exported squirrel data to {path}'))
