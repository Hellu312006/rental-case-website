from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds initial test users: admin, owner, tenant'

    def handle(self, *args, **options):
        self.stdout.write('Seeding test users...')

        # 1. Admin
        admin_email = 'admin@rentease.com'
        User.objects.filter(email=admin_email).delete()
        admin = User.objects.create_superuser(
            username=admin_email,
            email=admin_email,
            password='admin123',
            first_name='Admin',
            last_name='RentEase'
        )
        self.stdout.write(self.style.SUCCESS(f'Created Admin: {admin_email} / admin123'))

        # 2. Owner
        owner_email = 'owner@rentease.com'
        User.objects.filter(email=owner_email).delete()
        owner = User.objects.create_user(
            username=owner_email,
            email=owner_email,
            password='owner123',
            first_name='Alex',
            last_name='Morgan',
            role='Owner'
        )
        self.stdout.write(self.style.SUCCESS(f'Created Owner: {owner_email} / owner123'))

        # 3. Tenant
        tenant_email = 'tenant@rentease.com'
        User.objects.filter(email=tenant_email).delete()
        tenant = User.objects.create_user(
            username=tenant_email,
            email=tenant_email,
            password='tenant123',
            first_name='Jane',
            last_name='Tenant',
            role='Tenant'
        )
        self.stdout.write(self.style.SUCCESS(f'Created Tenant: {tenant_email} / tenant123'))
        
        self.stdout.write(self.style.SUCCESS('User seeding complete!'))
