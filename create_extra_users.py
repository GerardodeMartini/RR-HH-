import os
import django
import sys
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_project.settings')
django.setup()
from django.contrib.auth.models import User
from candidates.models import Candidate

def create_linked_user(username, email, candidate_name):
    # Check if user exists
    if not User.objects.filter(username=username).exists():
        u = User.objects.create_user(username, email, f'{username}123')
        print(f"CREATED USER: {username} / {username}123")
    else:
        u = User.objects.get(username=username)
        u.set_password(f'{username}123')
        u.save()
        print(f"UPDATED USER: {username}")

    # Find candidate and link
    try:
        # Searching by approximate name or file to be sure
        candidates = Candidate.objects.filter(first_name__icontains=candidate_name.split()[0])
        for c in candidates:
            if not c.user:
                c.user = u
                c.save()
                print(f"LINKED: {username} -> Candidate {c.first_name} {c.last_name}")
                return
        print(f"WARNING: Could not find unlinked candidate for {candidate_name}")
    except Exception as e:
        print(f"ERROR: {e}")

# 1. Maria Florencia Zubiani
create_linked_user('maria', 'maria@example.com', 'maria')

# 2. Gerardo de Martini
create_linked_user('gerardo', 'gerardo@example.com', 'gerardo')
