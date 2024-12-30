from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Doctor,Patient,Appointment,PatientDischargeDetails,Receptionist,Medicine
# Register your models here.
class DoctorAdmin(admin.ModelAdmin):
    pass
admin.site.register(Doctor, DoctorAdmin)

class PatientAdmin(admin.ModelAdmin):
    pass
admin.site.register(Patient, PatientAdmin)

class AppointmentAdmin(admin.ModelAdmin):
    pass
admin.site.register(Appointment, AppointmentAdmin)

class PatientDischargeDetailsAdmin(admin.ModelAdmin):
    pass
admin.site.register(PatientDischargeDetails, PatientDischargeDetailsAdmin)

class ReceptionistAdmin(admin.ModelAdmin):
    pass
admin.site.register(Receptionist,ReceptionistAdmin)
class MedicineAdmin(admin.ModelAdmin):
    pass
admin.site.register(Medicine,MedicineAdmin)
