
import os
import django
import sys

# Setup Django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_project.settings')
django.setup()

from django.contrib.auth.models import User
from clients.models import Company
from candidates.models import Candidate

def create_users():
    print("Setting up test users...")

    # 1. Admin / Owner
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print("CREATED: Admin user (admin/admin123)")
    else:
        u = User.objects.get(username='admin')
        u.set_password('admin123')
        u.save()
        print("UPDATED: Admin user password (admin/admin123)")

    # 2. Company
    if not User.objects.filter(username='empresa').exists():
        u = User.objects.create_user('empresa', 'empresa@example.com', 'empresa123')
        print("CREATED: Company user (empresa/empresa123)")
    else:
        u = User.objects.get(username='empresa')
        u.set_password('empresa123')
        u.save()
        print("UPDATED: Company user password (empresa/empresa123)")
    
    # Check/Create Company Profile
    if not hasattr(u, 'company_profile'):
        Company.objects.create(user=u, name="Empresa de Prueba", description="Una gran empresa")
        print("CREATED: Company profile for 'empresa'")

    # 3. Candidate
    # Rename old user if exists
    if User.objects.filter(username='candidato_demo').exists():
        u = User.objects.get(username='candidato_demo')
        u.username = 'candidato'
        u.save()
        print("RENAMED: 'candidato_demo' to 'candidato'")

    if not User.objects.filter(username='candidato').exists():
        u = User.objects.create_user('candidato', 'candidato@example.com', 'candidato123')
        print("CREATED: Candidate user (candidato/candidato123)")
    else:
        u = User.objects.get(username='candidato')
        # Ensure password is correct
        u.set_password('candidato123')
        u.save()
        print("UPDATED: Candidate user password")
        
    candidate, created = Candidate.objects.get_or_create(email='candidato@example.com', defaults={
        'first_name': 'Juan',
        'last_name': 'Perez'
    })
    
    # Link user to candidate
    candidate.user = u
    candidate.save()
    if created:
        print("CREATED: Candidate profile linked to 'candidato'")
    else:
        print("UPDATED: Linked existing candidate profile to 'candidato'")

if __name__ == '__main__':
    create_users()
