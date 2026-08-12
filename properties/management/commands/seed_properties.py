import io
import os
import urllib.request
from PIL import Image
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from properties.models import Property, PropertyCategory, City, Country, State

User = get_user_model()

def generate_mock_image(color=(37, 99, 235), name="mock.jpg"):
    # Generate a solid color image for mock fallback
    img = Image.new("RGB", (800, 600), color=color)
    f = io.BytesIO()
    img.save(f, format="JPEG")
    return ContentFile(f.getvalue(), name=name)

def download_image_from_internet(url, name="downloaded.jpg"):
    # Download open source photo from Unsplash with custom User-Agent
    req = urllib.request.Request(
        url,
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    )
    try:
        # 8-second timeout to prevent command hangs
        with urllib.request.urlopen(req, timeout=8) as response:
            return ContentFile(response.read(), name=name)
    except Exception as e:
        print(f"Skipping internet download for {name} (using local mock fallback): {e}")
        return None

class Command(BaseCommand):
    help = 'Seeds six sample properties with real internet photos or custom fallback images'

    def handle(self, *args, **options):
        self.stdout.write('Seeding sample properties with internet images...')

        # 1. Fetch default Owner
        try:
            owner = User.objects.get(email='owner@rentease.com')
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('Default owner owner@rentease.com not found. Please run seed_users first.'))
            return

        # 2. Setup properties dictionary
        mock_props = [
            {
                'name': 'Sunset paying guest house',
                'category': 'PG',
                'type': 'PG',
                'city': 'Surat',
                'address': 'Plot 42, Green Avenue, Surat, Gujarat',
                'rent': 6000,
                'deposit': 12000,
                'total': 6,
                'avail': 4,
                'color': (37, 99, 235),
                'url': 'https://images.unsplash.com/photo-1522771739844-6a9f6d5f14af?q=80&w=800&auto=format&fit=crop'
            },
            {
                'name': 'Alex Villa & Garden Suites',
                'category': 'House',
                'type': 'House',
                'city': 'Vadodara',
                'address': 'Row house #10, Heritage colony, Vadodara, Gujarat',
                'rent': 28000,
                'deposit': 50000,
                'total': 4,
                'avail': 2,
                'color': (5, 150, 105),
                'url': 'https://images.unsplash.com/photo-1512917774080-9991f1c4c750?q=80&w=800&auto=format&fit=crop'
            },
            {
                'name': 'Silicon Valley Premium Flat',
                'category': 'Flat',
                'type': 'Flat',
                'city': 'San Francisco',
                'address': 'Apt 4B, 500 Market St, San Francisco, California',
                'rent': 42000,
                'deposit': 85000,
                'total': 2,
                'avail': 1,
                'color': (15, 23, 42),
                'url': 'https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?q=80&w=800&auto=format&fit=crop'
            },
            {
                'name': 'LA Co-Living Student Hostel',
                'category': 'Hostel',
                'type': 'Hostel',
                'city': 'Los Angeles',
                'address': '1240 Westwood Blvd, Los Angeles, California',
                'rent': 9500,
                'deposit': 15000,
                'total': 12,
                'avail': 9,
                'color': (217, 119, 6),
                'url': 'https://images.unsplash.com/photo-1555854877-bab0e564b8d5?q=80&w=800&auto=format&fit=crop'
            },
            {
                'name': 'Ahmedabad heights residential unit',
                'category': 'Flat',
                'type': 'Flat',
                'city': 'Ahmedabad',
                'address': 'B-102, Shivalik Sky apartments, Ahmedabad, Gujarat',
                'rent': 18000,
                'deposit': 36000,
                'total': 3,
                'avail': 2,
                'color': (139, 92, 246),
                'url': 'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?q=80&w=800&auto=format&fit=crop'
            },
            {
                'name': 'Cozy Rajkot PG for students',
                'category': 'PG',
                'type': 'PG',
                'city': 'Rajkot',
                'address': 'Street 3, Moti tanki chowk, Rajkot, Gujarat',
                'rent': 5000,
                'deposit': 10000,
                'total': 5,
                'avail': 3,
                'color': (236, 72, 153),
                'url': 'https://images.unsplash.com/photo-1598928506311-c55ded91a20c?q=80&w=800&auto=format&fit=crop'
            }
        ]

        for p_data in mock_props:
            # Clean up duplicates to force update with real images
            Property.objects.filter(property_name=p_data['name']).delete()

            try:
                category = PropertyCategory.objects.get(category_name=p_data['category'])
            except PropertyCategory.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"Category {p_data['category']} not found, skipping {p_data['name']}."))
                continue

            try:
                city = City.objects.get(name=p_data['city'])
            except City.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"City {p_data['city']} not found in database, skipping {p_data['name']}."))
                continue

            state = city.state
            country = state.country

            # Create property
            prop = Property.objects.create(
                owner=owner,
                category=category,
                property_name=p_data['name'],
                property_type=p_data['type'],
                description=f"A premium and beautiful {p_data['type']} listing located in {p_data['city']}. Offering exceptional modern layouts, walking access to local shopping markets, high-speed fiber internet connection, and absolute security.",
                address=p_data['address'],
                city=city,
                state=state,
                country=country,
                rent_per_month=p_data['rent'],
                security_deposit=p_data['deposit'],
                total_rooms=p_data['total'],
                available_rooms=p_data['avail'],
            )

            file_name = f"seed_{p_data['type']}_{p_data['city']}.jpg"
            
            # Attempt to download real open-source photo
            image_file = download_image_from_internet(p_data['url'], name=file_name)
            
            if image_file:
                prop.image.save(file_name, image_file, save=True)
                self.stdout.write(self.style.SUCCESS(f"Created property with Unsplash Photo: {p_data['name']}"))
            else:
                # Fallback to local colored mock
                mock_file = generate_mock_image(color=p_data['color'], name=file_name)
                prop.image.save(file_name, mock_file, save=True)
                self.stdout.write(self.style.SUCCESS(f"Created property with fallback image: {p_data['name']}"))

        self.stdout.write(self.style.SUCCESS('Property seeding complete!'))

