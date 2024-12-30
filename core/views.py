from rest_framework import viewsets, permissions
from .models import Doctor, Patient, Appointment, PatientDischargeDetails, Receptionist, Medicine
from .serializers import (
    DoctorSerializer,
    PatientSerializer,
    AppointmentSerializer,
    PatientDischargeDetailsSerializer,
    ReceptionistSerializer,
    MedicineSerializer,
)
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticatedOrReadOnly,IsAuthenticated
from .permissions import IsAdminOrReceptionist


class BaseViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminOrReceptionist,)  # Use only the custom permission

    def create(self, request, *args, **kwargs):
        # Custom logic for create if needed
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        # Custom logic for update if needed
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        # Custom logic for destroy if needed
        return super().destroy(request, *args, **kwargs)


class DoctorViewSet(BaseViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer

class PatientViewSet(BaseViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = (IsAuthenticated, IsAdminOrReceptionist)

from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from .models import Appointment, Patient
from .serializers import AppointmentSerializer
from rest_framework.decorators import action
from .serializers import AppointmentStatusUpdateSerializer
class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        
        # Allow patients to see their appointments
        if hasattr(user, 'patient'):
            return Appointment.objects.filter(patient=user.patient)

        # Allow doctors to see their appointments
        if hasattr(user, 'doctor'):
            return Appointment.objects.filter(doctor=user.doctor)

        # Admins and receptionists see all appointments
        return Appointment.objects.all()

    def perform_create(self, serializer):
        user = self.request.user

        # Logic for staff (admins)
        if user.is_staff:
            patient_id = self.request.data.get('patient')  # Get patient ID from request data
            if patient_id:
                try:
                    patient = Patient.objects.get(id=patient_id)
                except Patient.DoesNotExist:
                    raise PermissionDenied("Patient not found.")
                
                serializer.save(patient=patient)
            else:
                raise PermissionDenied("Patient ID must be provided.")
        
        # Logic for receptionists and patients
        elif user.groups.filter(name='Receptionists').exists() or hasattr(user, 'patient'):
            patient = user.patient if hasattr(user, 'patient') else None
            
            if patient is None:
                raise PermissionDenied("You do not have a valid patient associated with your account.")
            
            # Ensure patients can only create appointments for themselves
            if hasattr(user, 'patient'):
                # Set the patient to the one associated with the user
                serializer.save(patient=patient)
            else:
                raise PermissionDenied("You do not have permission to book an appointment.")
        
        else:
            raise PermissionDenied("You do not have permission to book an appointment.")


    @action(detail=False, methods=['get'], permission_classes=[IsAdminOrReceptionist])
    def pending(self, request):
        pending_appointments = Appointment.objects.filter(status='Pending')
        serializer = self.get_serializer(pending_appointments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminOrReceptionist])
    def approve(self, request, pk=None):
        appointment = self.get_object()
    
    # Check if the appointment is already approved or rejected
        if appointment.status in ['Scheduled', 'Rejected']:
            return Response({'error': 'This appointment has already been processed.'}, status=status.HTTP_400_BAD_REQUEST)

    # Fetch appointment details
        appointment_details = AppointmentSerializer(appointment).data
    
    # Prepare the response data including appointment details
        response_data = {
           'appointment_details': appointment_details,
           ' message': 'Please confirm the approval by providing the appointment date.',
    }

    # Check if the request contains a confirmation flag
        if request.data.get('confirm'):
            appointment_date = request.data.get('appointment_date')
            doctor_id = request.data.get('doctor_id') 
            if not appointment_date:
                raise ValidationError("Appointment date must be provided.")
            if not doctor_id:
                raise ValidationError("Doctor ID must be provided.")

        # Set the appointment date and change the status to Scheduled
            appointment.appointment_date = appointment_date
            appointment.status = 'Scheduled'
            try:
                appointment.doctor = Doctor.objects.get(id=doctor_id)  # Assuming you have a Doctor model
            except Doctor.DoesNotExist:
                raise ValidationError("Doctor with the specified ID does not exist.")  # Change this line
            appointment.save()

            response_data.update({
            'status': 'Appointment approved',
            'appointment_date': appointment.appointment_date,
            'doctor_id': appointment.doctor.id
            })

        return Response(response_data, status=status.HTTP_200_OK)


    @action(detail=True, methods=['post'], permission_classes=[IsAdminOrReceptionist])
    def reject(self, request, pk=None):
        appointment = self.get_object()
    
    # Check if the appointment is already approved or rejected
        if appointment.status in ['Scheduled', 'Rejected']:
            return Response({'error': 'This appointment has already been processed.'}, status=status.HTTP_400_BAD_REQUEST)

    # Fetch appointment details
        appointment_details = AppointmentSerializer(appointment).data
    
    # Prepare the response data including appointment details
        response_data = {
            'appointment_details': appointment_details,
            'message': 'Please confirm the rejection.',
        }

    # Check if the request contains a confirmation flag
        if request.data.get('confirm'):
            appointment.status = 'Rejected'
            appointment.save()
            response_data.update({'status': 'Appointment rejected'})

        return Response(response_data, status=status.HTTP_200_OK)


    @action(detail=True, methods=['post'], permission_classes=[IsAdminOrReceptionist])
    def update_status(self, request, pk=None):
        appointment = self.get_object()  # Retrieve the appointment instance
        serializer = AppointmentStatusUpdateSerializer(appointment, data=request.data)

        if serializer.is_valid():
            serializer.save()  # Save updates to the appointment
            return Response({'status': f'Appointment status updated to {serializer.validated_data["status"]}'}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)






from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import PatientDischargeDetails, Appointment
from .serializers import PatientDischargeDetailsSerializer
from rest_framework.exceptions import ValidationError

class PatientDischargeView(viewsets.ModelViewSet):
    serializer_class=PatientDischargeDetailsSerializer
    queryset=PatientDischargeDetails.objects.all()

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            if user.is_staff or hasattr(user,"receptionist"):
                return PatientDischargeDetails.objects.all()
            if hasattr(user, 'patient'):
                return PatientDischargeDetails.objects.filter(patient=user.patient)
            if hasattr(user,'doctor'):
                return PatientDischargeDetails.objects.filter(assigned_doctor_name=user.doctor)
        return PatientDischargeDetails.objects.none()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Call the discharge method from the serializer to create discharge details
            discharge_details = serializer.create(serializer.validated_data)
            return Response(PatientDischargeDetailsSerializer(discharge_details).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        discharge_detail = self.get_object()
        return Response(PatientDischargeDetailsSerializer(discharge_detail).data)

    def update(self, request, *args, **kwargs):
        discharge_detail = self.get_object()
        serializer = self.get_serializer(discharge_detail, data=request.data, partial=True)

        if serializer.is_valid():
            updated_discharge_detail = serializer.save()
            return Response(PatientDischargeDetailsSerializer(updated_discharge_detail).data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        discharge_detail = self.get_object()
        discharge_detail.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



# from rest_framework import viewsets, status
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# from .models import PatientDischargeDetails, Patient
# from .serializers import PatientDischargeDetailsSerializer

# class PatientDischargeView(viewsets.ViewSet):
#     permission_classes = [IsAuthenticated]
#     queryset = PatientDischargeDetails.objects.all()
#     serializer_class = PatientDischargeDetailsSerializer

#     # def create(self, request):
#     #     print(request)
#     #     patient_id = request.data.get('patient_id')

#     #     try:
#     #         patient = Patient.objects.get(id=patient_id)
#     #     except Patient.DoesNotExist:
#     #         return Response({"error": "Patient not found."}, status=status.HTTP_404_NOT_FOUND)

#     #     serializer = self.get_serializer(data=request.data)
#     #     if serializer.is_valid():
#     #         discharge_details = serializer.save(patient=patient)
#     #         return Response(serializer(discharge_details), status=status.HTTP_201_CREATED)

#     #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)






class ReceptionistViewSet(BaseViewSet):
    queryset = Receptionist.objects.all()
    serializer_class = ReceptionistSerializer

class MedicineViewSet(BaseViewSet):
    queryset = Medicine.objects.all()
    serializer_class = MedicineSerializer



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import PatientDischargeDetails, Patient
from .serializers import PatientDischargeDetailsSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

class DownloadBillView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, format=None):
        try:
            # Check if the user is an admin or receptionist
            if request.user.is_staff or (hasattr(request.user, 'role') and request.user.role == 'receptionist'):
                # Admin or receptionist can access any patient's discharge details
                discharge_details = PatientDischargeDetails.objects.filter(patientId=pk).order_by('-id')[:1]
            else:
                # Only allow the patient to access their own discharge details
                patient = Patient.objects.get(user=request.user)  # Get the logged-in patient
                discharge_details = PatientDischargeDetails.objects.filter(patientId=patient.id).order_by('-id')[:1]

            if not discharge_details.exists():
                return Response({"error": "Discharge details not found."}, status=status.HTTP_404_NOT_FOUND)

            discharge_detail = discharge_details[0]  # Get the latest discharge detail
            
            # Serialize the discharge detail
            serializer = PatientDischargeDetailsSerializer(discharge_detail)

            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Patient.DoesNotExist:
            return Response({"error": "Patient not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

