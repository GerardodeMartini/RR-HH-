from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from candidates.models import Candidate
from clients.models import Company, Vacancy
from applications.models import Application, Answer

class Command(BaseCommand):
    help = 'Borra todos los candidatos, empresas, vacantes, postulaciones y usuarios que no sean superusuarios o staff.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Iniciando borrado de datos de prueba...'))

        # Borramos las entidades en orden para evitar problemas de relación cruzada aunque cascada las borra igual
        ans_count, _ = Answer.objects.all().delete()
        app_count, _ = Application.objects.all().delete()
        vac_count, _ = Vacancy.objects.all().delete()
        comp_count, _ = Company.objects.all().delete()
        cand_count, _ = Candidate.objects.all().delete()

        # Borramos sólo los usuarios que NO son ni superusuarios ni parte del staff
        users_deleted, dict_details = User.objects.filter(is_superuser=False, is_staff=False).delete()

        self.stdout.write(self.style.SUCCESS(f'Base de datos limpiada correctamente:'))
        self.stdout.write(f'- {cand_count} Candidatos eliminados')
        self.stdout.write(f'- {comp_count} Empresas eliminadas')
        self.stdout.write(f'- {vac_count} Vacantes eliminadas')
        self.stdout.write(f'- {app_count} Postulaciones eliminadas')
        self.stdout.write(f'- {users_deleted} Usuarios eliminados')
        
        staff_count = User.objects.filter(is_staff=True).count()
        self.stdout.write(self.style.SUCCESS(f'>> Conservados {staff_count} usuarios administrativos / superusers.'))
