from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import (
    DoctorViewSet,
    PatientViewSet,
    AppointmentViewSet,
    PatientDischargeView,
    ReceptionistViewSet,
    MedicineViewSet,
    # UserViewSet,
)

router = SimpleRouter()
router.register(r'doctors', DoctorViewSet)
router.register(r'patients', PatientViewSet)
router.register(r'appointments', AppointmentViewSet)
router.register(r'discharge-details', PatientDischargeView, basename='patientdischarge')
router.register(r'receptionists', ReceptionistViewSet)
router.register(r'medicines', MedicineViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
