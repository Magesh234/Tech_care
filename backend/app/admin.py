from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import (
    User, Patient, Doctor, 
    DiagnosisHistory, DiagnosticList, 
    LabResult, Appointment
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'user_type', 'is_staff', 'is_active')
    list_filter = ('user_type', 'is_staff', 'is_active')
    search_fields = ('email', 'first_name', 'last_name', 'phone_number')
    ordering = ('email',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'phone_number', 'profile_picture')}),
        (_('User type'), {'fields': ('user_type',)}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'user_type', 'is_active', 'is_staff')
        }),
    )


class PatientInline(admin.StackedInline):
    model = Patient
    can_delete = False
    verbose_name_plural = _('Patient Details')
    fk_name = 'user'


class DoctorInline(admin.StackedInline):
    model = Doctor
    can_delete = False
    verbose_name_plural = _('Doctor Details')
    fk_name = 'user'


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'gender', 'date_of_birth', 'age', 'insurance_type')
    list_filter = ('gender', 'insurance_type')
    search_fields = ('user__first_name', 'user__last_name', 'user__email')
    readonly_fields = ('id', 'age')
    raw_id_fields = ('user',)
    
    fieldsets = (
        (_('Identity'), {'fields': ('id', 'user')}),
        (_('Personal Info'), {'fields': ('gender', 'date_of_birth', 'age')}),
        (_('Medical Info'), {'fields': ('insurance_type', 'emergency_contact')}),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'specialization', 'license_number', 'years_of_experience', 'accepting_new_patients')
    list_filter = ('specialization', 'accepting_new_patients')
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'license_number')
    readonly_fields = ('id',)
    raw_id_fields = ('user',)
    
    fieldsets = (
        (_('Identity'), {'fields': ('id', 'user')}),
        (_('Professional Info'), {'fields': ('specialization', 'license_number', 'years_of_experience')}),
        (_('Status'), {'fields': ('accepting_new_patients',)}),
        (_('Biography'), {'fields': ('biography',)}),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(DiagnosisHistory)
class DiagnosisHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient_name', 'doctor_name', 'month', 'year', 'systolic_status', 'diastolic_status', 'heart_rate_status')
    list_filter = ('month', 'year', 'blood_pressure_systolic_levels', 'blood_pressure_diastolic_levels', 'heart_rate_levels')
    search_fields = ('patient__user__first_name', 'patient__user__last_name', 'doctor__user__last_name')
    raw_id_fields = ('patient', 'doctor')
    
    fieldsets = (
        (_('Basic Info'), {'fields': ('id', 'patient', 'doctor', 'month', 'year')}),
        (_('Blood Pressure'), {'fields': (
            'blood_pressure_systolic_value', 'blood_pressure_systolic_levels',
            'blood_pressure_diastolic_value', 'blood_pressure_diastolic_levels'
        )}),
        (_('Vital Signs'), {'fields': (
            'heart_rate_value', 'heart_rate_levels',
            'respiratory_rate_value', 'respiratory_rate_levels',
            'temperature_value', 'temperature_levels'
        )}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at')}),
    )
    
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    def patient_name(self, obj):
        return obj.patient.name
    patient_name.short_description = _('Patient')
    patient_name.admin_order_field = 'patient__user__last_name'
    
    def doctor_name(self, obj):
        return obj.doctor.name if obj.doctor else '-'
    doctor_name.short_description = _('Doctor')
    doctor_name.admin_order_field = 'doctor__user__last_name'
    
    def systolic_status(self, obj):
        return obj.get_blood_pressure_systolic_levels_display()
    systolic_status.short_description = _('Systolic Status')
    systolic_status.admin_order_field = 'blood_pressure_systolic_levels'
    
    def diastolic_status(self, obj):
        return obj.get_blood_pressure_diastolic_levels_display()
    diastolic_status.short_description = _('Diastolic Status')
    diastolic_status.admin_order_field = 'blood_pressure_diastolic_levels'
    
    def heart_rate_status(self, obj):
        return obj.get_heart_rate_levels_display()
    heart_rate_status.short_description = _('Heart Rate Status')
    heart_rate_status.admin_order_field = 'heart_rate_levels'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('patient__user', 'doctor__user')


@admin.register(DiagnosticList)
class DiagnosticListAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient_name', 'doctor_name', 'name', 'status', 'diagnosed_date')
    list_filter = ('status', 'diagnosed_date')
    search_fields = ('patient__user__first_name', 'patient__user__last_name', 'doctor__user__last_name', 'name')
    raw_id_fields = ('patient', 'doctor')
    
    fieldsets = (
        (_('Basic Info'), {'fields': ('id', 'patient', 'doctor')}),
        (_('Diagnosis Details'), {'fields': ('name', 'description', 'status', 'diagnosed_date')}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at')}),
    )
    
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    def patient_name(self, obj):
        return obj.patient.name
    patient_name.short_description = _('Patient')
    patient_name.admin_order_field = 'patient__user__last_name'
    
    def doctor_name(self, obj):
        return obj.doctor.name if obj.doctor else '-'
    doctor_name.short_description = _('Doctor')
    doctor_name.admin_order_field = 'doctor__user__last_name'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('patient__user', 'doctor__user')


@admin.register(LabResult)
class LabResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient_name', 'doctor_name', 'name', 'result_value', 'result_unit', 'status', 'performed_date')
    list_filter = ('status', 'performed_date', 'reported_date')
    search_fields = ('patient__user__first_name', 'patient__user__last_name', 'doctor__user__last_name', 'name')
    raw_id_fields = ('patient', 'doctor')
    
    fieldsets = (
        (_('Basic Info'), {'fields': ('id', 'patient', 'doctor')}),
        (_('Test Details'), {'fields': ('name', 'result_value', 'result_unit', 'reference_range', 'status')}),
        (_('Dates'), {'fields': ('performed_date', 'reported_date')}),
        (_('Additional Info'), {'fields': ('notes',)}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at')}),
    )
    
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    def patient_name(self, obj):
        return obj.patient.name
    patient_name.short_description = _('Patient')
    patient_name.admin_order_field = 'patient__user__last_name'
    
    def doctor_name(self, obj):
        return obj.doctor.name if obj.doctor else '-'
    doctor_name.short_description = _('Doctor')
    doctor_name.admin_order_field = 'doctor__user__last_name'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('patient__user', 'doctor__user')


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient_name', 'doctor_name', 'appointment_date', 'appointment_time', 'appointment_type', 'status')
    list_filter = ('status', 'appointment_type', 'appointment_date')
    search_fields = ('patient__user__first_name', 'patient__user__last_name', 'doctor__user__last_name', 'reason')
    raw_id_fields = ('patient', 'doctor')
    
    fieldsets = (
        (_('Basic Info'), {'fields': ('id', 'patient', 'doctor')}),
        (_('Appointment Details'), {'fields': ('appointment_date', 'appointment_time', 'appointment_type', 'status')}),
        (_('Additional Info'), {'fields': ('reason', 'notes')}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at')}),
    )
    
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    def patient_name(self, obj):
        return obj.patient.name
    patient_name.short_description = _('Patient')
    patient_name.admin_order_field = 'patient__user__last_name'
    
    def doctor_name(self, obj):
        return obj.doctor.name
    doctor_name.short_description = _('Doctor')
    doctor_name.admin_order_field = 'doctor__user__last_name'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('patient__user', 'doctor__user')