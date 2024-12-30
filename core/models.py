from django.db import models
from django.contrib.auth import get_user_model
from main import settings
from django.core.validators import RegexValidator

# Define department choices as a constant for reuse
DEPARTMENTS = [
    ('Cardiologist', 'Cardiologist'),
    ('Dermatologists', 'Dermatologists'),
    ('Emergency Medicine Specialists', 'Emergency Medicine Specialists'),
    ('Allergists/Immunologists', 'Allergists/Immunologists'),
    ('Anesthesiologists', 'Anesthesiologists'),
    ('Colon and Rectal Surgeons', 'Colon and Rectal Surgeons'),
]

# Custom user model
from user.models import User

class Doctor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='profile_pic/DoctorProfilePic/', null=True, blank=True)
    address = models.CharField(max_length=40)
    mobile = models.CharField(max_length=20, null=True, validators=[RegexValidator(r'^\+?1?\d{9,15}$')])
    department = models.CharField(max_length=50, choices=DEPARTMENTS, default='Cardiologist')
    status = models.BooleanField(default=False)

    @property
    def get_name(self):
        return f"{self.user.first_name} {self.user.last_name}"

    def __str__(self):
        return f"{self.user.first_name} ({self.department})"


from django.core.validators import RegexValidator
from django.db import models
from django.conf import settings

class Patient(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='profile_pic/PatientProfilePic/', null=True, blank=True)
    address = models.CharField(max_length=40)
    mobile = models.CharField(
        max_length=20, 
        null=True, 
        validators=[RegexValidator(r'^\+?1?\d{9,15}$')]
    )
    symptoms = models.CharField(max_length=100, null=False)
    assigned_doctor = models.ForeignKey(Doctor, null=True, on_delete=models.SET_NULL)
    admit_date = models.DateField(auto_now_add=True)  # Automatically set the date on creation
    status = models.BooleanField(default=False)

    @property
    def get_name(self):
        return f"{self.user.first_name} {self.user.last_name}"

    def __str__(self):
        return f"{self.user.first_name} ({self.symptoms})"



from django.db import models

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)  # Required
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, null=True, blank=True)  # Optional
    booked_date = models.DateTimeField(auto_now_add=True,blank=True)      # DateTimeField for both date and time
    description = models.TextField(max_length=500)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='scheduled')
    emergency = models.BooleanField(default=False)
    appointment_date = models.DateTimeField(blank=True, null=True) 

    def __str__(self):
        return f"Appointment for {self.patient} with {'No Doctor' if not self.doctor else self.doctor} on {self.booked_date.strftime('%Y-%m-%d %H:%M:%S')}"


class PatientDischargeDetails(models.Model):
    patient = models.ForeignKey(Patient, null=True, on_delete=models.SET_NULL)
    assigned_doctor_name = models.CharField(max_length=40,default="samriddha")
    address = models.CharField(max_length=40)
    mobile = models.CharField(max_length=20, null=True, validators=[RegexValidator(r'^\+?1?\d{9,15}$')])
    symptoms = models.CharField(max_length=100, null=True)
    admit_date = models.DateField(null=False,default=1)
    release_date = models.DateField(null=False,default=1)
    day_spent = models.PositiveIntegerField(null=False,default=1)
    room_charge = models.PositiveIntegerField(null=False,default=1)
    medicine_cost = models.PositiveIntegerField(null=False,default=1)
    doctor_fee = models.PositiveIntegerField(null=False,default=1)
    other_charge = models.PositiveIntegerField(null=False,default=1)
    total = models.PositiveIntegerField(null=False)


class Receptionist(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='profile_pic/ReceptionistProfilePic/', null=True, blank=True)
    address = models.CharField(max_length=40)
    mobile = models.CharField(max_length=20, null=True, validators=[RegexValidator(r'^\+?1?\d{9,15}$')])
    status = models.BooleanField(default=False)

    @property
    def get_name(self):
        return f"{self.user.first_name} {self.user.last_name}"

    def __str__(self):
        return self.user.first_name



class Medicine(models.Model):
    name = models.CharField(max_length=100, unique=True)
    dosage = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField()
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.dosage})"

    class Meta:
        verbose_name_plural = "Medicines"
