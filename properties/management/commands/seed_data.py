from django.core.management.base import BaseCommand
from properties.models import Country, State, City, PropertyCategory

class Command(BaseCommand):
    help = 'Seeds initial locations (Countries, States, Cities) and Property Categories'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database...')

        # 1. Seed Countries, States, Cities
        # Country: India
        india, _ = Country.objects.get_or_create(name='India')
        
        # State: Gujarat
        gujarat, _ = State.objects.get_or_create(country=india, name='Gujarat')
        for city_name in ['Surat', 'Ahmedabad', 'Vadodara', 'Rajkot']:
            City.objects.get_or_create(state=gujarat, name=city_name)
            
        # State: Maharashtra
        maharashtra, _ = State.objects.get_or_create(country=india, name='Maharashtra')
        for city_name in ['Mumbai', 'Pune', 'Nagpur']:
            City.objects.get_or_create(state=maharashtra, name=city_name)

        # Country: USA
        usa, _ = Country.objects.get_or_create(name='USA')
        
        # State: California
        california, _ = State.objects.get_or_create(country=usa, name='California')
        for city_name in ['Los Angeles', 'San Francisco', 'San Diego']:
            City.objects.get_or_create(state=california, name=city_name)
            
        # State: Texas
        texas, _ = State.objects.get_or_create(country=usa, name='Texas')
        for city_name in ['Austin', 'Houston', 'Dallas']:
            City.objects.get_or_create(state=texas, name=city_name)

        self.stdout.write(self.style.SUCCESS('Successfully seeded countries, states, and cities!'))

        # 2. Seed Property Categories
        categories = [
            {
                'name': 'PG',
                'description': 'Paying Guest accommodations, ideal for students and single working professionals with shared facilities.',
            },
            {
                'name': 'Flat',
                'description': 'Modern apartment units, ranging from 1 BHK to luxury multi-room configurations in residential societies.',
            },
            {
                'name': 'House',
                'description': 'Independent houses and villas offering complete privacy, spacious rooms, yards, and dedicated parking.',
            },
            {
                'name': 'Hostel',
                'description': 'Dormitory and shared student housing listings, generally close to colleges and academic hubs.',
            }
        ]

        for cat in categories:
            # We don't require an image to exist or be seeded, but category_name is unique
            obj, created = PropertyCategory.objects.get_or_create(
                category_name=cat['name'],
                defaults={'description': cat['description']}
            )
            if not created:
                obj.description = cat['description']
                obj.save()

        self.stdout.write(self.style.SUCCESS('Successfully seeded Property Categories!'))
        self.stdout.write(self.style.SUCCESS('Seeding complete!'))
