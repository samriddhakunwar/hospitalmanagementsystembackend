from rest_framework import serializers
from .models import Doctor, Receptionist, Patient, PatientDischargeDetails, Medicine, Appointment
from django.contrib.auth import get_user_model
from datetime import date
from user.serializers import UserSerializer
from user.models import User

class DoctorSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Doctor
        fields = (
            'id',
            'user',
            'profile_pic',
            'address',
            'mobile',
            'department',
            'status',
        )

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = UserSerializer().create(user_data)
        return Doctor.objects.create(user=user, **validated_data)

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if user_data:
            for attr, value in user_data.items():
                setattr(instance.user, attr, value)
            instance.user.save()

        return instance


from rest_framework import serializers
from .models import Patient, Doctor

class PatientSerializer(serializers.ModelSerializer):
    assigned_doctor = serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.all(), allow_null=True)

    class Meta:
        model = Patient
        fields = (
            'id',
            'user',
            'profile_pic',
            'address',
            'mobile',
            'symptoms',
            'assigned_doctor',  # This references the ForeignKey to Doctor
            'admit_date',
            'status',
        )
        read_only_fields = ('id', 'admit_date',)

    def create(self, validated_data):
        return super().create(validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance



class ReceptionistSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Receptionist
        fields = (
            'id',
            'user',
            'profile_pic',
            'address',
            'mobile',
            'status',
        )
        read_only_fields = ('id',)

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = UserSerializer().create(user_data)
        return Receptionist.objects.create(user=user, **validated_data)

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if user_data:
            for attr, value in user_data.items():
                setattr(instance.user, attr, value)
            instance.user.save()

        return instance



from rest_framework import serializers
from .models import Appointment, Doctor, Patient
from rest_framework.exceptions import ValidationError
class DoctorNameField(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        # Override this method to return the queryset based on names
        return Doctor.objects.all()

    def to_internal_value(self, data):
        # Convert name to an instance
        if isinstance(data, str):
            try:
                return self.get_queryset().get(name=data)  # Adjust the field as needed
            except Doctor.DoesNotExist:
                raise serializers.ValidationError(f"Doctor with name '{data}' does not exist.")
        return super().to_internal_value(data)

class PatientNameField(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        # Override this method to return the queryset based on names
        return Patient.objects.all()

    def to_internal_value(self, data):
        # Convert name to an instance
        if isinstance(data, str):
            try:
                return self.get_queryset().get(name=data)  # Adjust the field as needed
            except Patient.DoesNotExist:
                raise serializers.ValidationError(f"Patient with name '{data}' does not exist.")
        return super().to_internal_value(data)
    

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Appointment, Patient  # Make sure to import your models

class AppointmentSerializer(serializers.ModelSerializer):
    patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all(), required=True)
    doctor = DoctorNameField(required=False, allow_null=True)

    class Meta:
        model = Appointment
        fields = (
            'id',
            'patient',
            'doctor',
            'booked_date',
            'description',
            'status',
            'emergency',
            'appointment_date',
        )
        read_only_fields = ('booked_date', 'status','appointment_date')

    def create(self, validated_data):
        # No need to fetch patient by name, since PrimaryKeyRelatedField handles this
        validated_data['status'] = 'Pending'  # Set status to Pending
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'patient' in validated_data:
            # If you want to allow updates by name, handle that here
            instance.patient = validated_data.pop('patient')
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance





# class PatientDischargeDetailsSerializer(serializers.ModelSerializer):
#     patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all())
#     assigned_doctor = serializers.CharField(source='assigned_doctor_name')

#     class Meta:
#         model = PatientDischargeDetails
#         fields = (
#             'id',
#             'patient',
#             'assigned_doctor',
#             'address',
#             'mobile',
#             'symptoms',
#             'admit_date',
#             'release_date',
#             'day_spent',
#             'room_charge',
#             'medicine_cost',
#             'doctor_fee',
#             'other_charge',
#             'total',
#         )
#         read_only_fields = ('id',)

#     def discharge(self, validated_data):
#         patient = validated_data['patient']

#         # Check for completed appointments
#         completed_appointments = Appointment.objects.filter(patient=patient, status='completed')
#         if not completed_appointments.exists():
#             raise ValidationError("The patient must have at least one completed appointment before discharge.")

#         today = date.today()
#         days = (today - validated_data['admit_date']).days
#         total = self.calculate_total(validated_data, days)

#         # Create discharge details
#         discharge_details = PatientDischargeDetails.objects.create(
#             patient=patient,
#             assigned_doctor_name=validated_data.get('assigned_doctor_name', ''),
#             address=validated_data['address'],
#             mobile=validated_data['mobile'],
#             symptoms=validated_data['symptoms'],
#             admit_date=validated_data['admit_date'],
#             release_date=today,
#             day_spent=days,
#             room_charge=validated_data.get('room_charge', 0),
#             medicine_cost=validated_data.get('medicine_cost', 0),
#             doctor_fee=validated_data.get('doctor_fee', 0),
#             other_charge=validated_data.get('other_charge', 0),
#             total=total,
#         )

#         # Delete completed appointments
#         completed_appointments.delete()

#         return discharge_details

#     def calculate_total(self, validated_data, days):
#         room_charge = validated_data.get('room_charge', 0) * days
#         doctor_fee = validated_data.get('doctor_fee', 0)
#         medicine_cost = validated_data.get('medicine_cost', 0)
#         other_charge = validated_data.get('other_charge', 0)
#         return room_charge + doctor_fee + medicine_cost + other_charge


from rest_framework import serializers
from .models import PatientDischargeDetails, Appointment
from rest_framework.exceptions import ValidationError
from datetime import date

class PatientDischargeDetailsSerializer(serializers.ModelSerializer):
    patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all())
    assigned_doctor = serializers.CharField(source='assigned_doctor_name')

    class Meta:
        model = PatientDischargeDetails
        fields = (
            'id',
            'patient',
            'assigned_doctor',
            'address',
            'mobile',
            'symptoms',
            'admit_date',
            'release_date',
            'day_spent',
            'room_charge',
            'medicine_cost',
            'doctor_fee',
            'other_charge',
            'total',
        )
        read_only_fields = ('id',)

    def create(self, validated_data):
        patient = validated_data['patient']

        # Check for completed appointments
        completed_appointments = Appointment.objects.filter(patient=patient, status='completed')
        if not completed_appointments.exists():
            raise ValidationError("The patient must have at least one completed appointment before discharge.")

        today = date.today()
        days = (today - validated_data['admit_date']).days

        # Set release date and total
        validated_data['release_date'] = today
        validated_data['day_spent'] = days
        validated_data['total'] = self.calculate_total(validated_data, days)

        # Create discharge details
        discharge_details = PatientDischargeDetails.objects.create(**validated_data)

        # Delete completed appointments
        completed_appointments.delete()

        return discharge_details

    def calculate_total(self, validated_data, days):
        room_charge = validated_data.get('room_charge', 0) * days
        doctor_fee = validated_data.get('doctor_fee', 0)
        medicine_cost = validated_data.get('medicine_cost', 0)
        other_charge = validated_data.get('other_charge', 0)
        total = room_charge + doctor_fee + medicine_cost + other_charge
        return total
    



class MedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = (
            'id',
            'name',
            'dosage',
            'price',
            'stock_quantity',
            'description',
        )
        read_only_fields = ('id',)

    def validate_name(self, value):
        if Medicine.objects.filter(name=value).exists():
            raise serializers.ValidationError("This medicine name already exists.")
        return value

    def create(self, validated_data):
        return super().create(validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

from rest_framework import serializers
from .models import Appointment

class AppointmentStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['status']

    def validate_status(self, value):
        # Allow only specific status changes
        allowed_statuses = ['Scheduled', 'Canceled','completed',]  # Add more statuses as needed
        if value not in allowed_statuses:
            raise serializers.ValidationError(f"Status must be one of: {', '.join(allowed_statuses)}.")
        return value

