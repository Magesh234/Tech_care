from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser, BaseUserManager
import uuid


class UserManager(BaseUserManager):
    """
    Custom user manager for handling both Patient and Doctor user creation
    """
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('Users must have an email address'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('user_type', 'admin')

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Base user model for authentication system
    Extends Django's AbstractUser to add role-based permissions
    """
    USER_TYPE_CHOICES = [
        ('patient', _('Patient')),
        ('doctor', _('Doctor')),
        ('admin', _('Administrator')),
    ]

    username = None  # Remove username field
    email = models.EmailField(_('Email Address'), unique=True)
    user_type = models.CharField(_('User Type'), max_length=10, choices=USER_TYPE_CHOICES)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$', 
        message=_("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    )
    phone_number = models.CharField(
        _('Phone Number'), 
        validators=[phone_regex], 
        max_length=17, 
        blank=True
    )
    profile_picture = models.URLField(_('Profile Picture'), blank=True, null=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'user_type']

    objects = UserManager()

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['email']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['user_type']),
        ]

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    @property
    def full_name(self):
        return self.get_full_name()


class Patient(models.Model):
    """
    Model representing a patient in the healthcare system.
    Extends the User model with patient-specific information.
    """
    GENDER_CHOICES = [
        ('M', _('Male')),
        ('F', _('Female')),
        ('O', _('Other')),
    ]
    
    INSURANCE_CHOICES = [
        ('private', _('Private')),
        ('medicare', _('Medicare')),
        ('medicaid', _('Medicaid')),
        ('uninsured', _('Uninsured')),
        ('other', _('Other')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='patient_profile',
        limit_choices_to={'user_type': 'patient'}
    )
    gender = models.CharField(_('Gender'), max_length=1, choices=GENDER_CHOICES)
    date_of_birth = models.DateField(_('Date of Birth'))
    emergency_contact = models.CharField(
        _('Emergency Contact'),
        validators=[User.phone_regex],
        max_length=17,
        blank=True
    )
    insurance_type = models.CharField(
        _('Insurance Type'),
        max_length=20,
        choices=INSURANCE_CHOICES,
        default='private'
    )
    
    class Meta:
        verbose_name = _('Patient')
        verbose_name_plural = _('Patients')
        ordering = ['user__last_name', 'user__first_name']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['date_of_birth']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.id})"
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('patient-detail', args=[str(self.id)])
    
    @property
    def name(self):
        return self.user.get_full_name()
    
    @property
    def age(self):
        """Calculate age from date of birth."""
        from datetime import date
        today = date.today()
        born = self.date_of_birth
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


class Doctor(models.Model):
    """
    Model representing a doctor in the healthcare system.
    Extends the User model with doctor-specific information.
    """
    SPECIALIZATION_CHOICES = [
        ('general_practitioner', _('General Practitioner')),
        ('cardiologist', _('Cardiologist')),
        ('dermatologist', _('Dermatologist')),
        ('endocrinologist', _('Endocrinologist')),
        ('gastroenterologist', _('Gastroenterologist')),
        ('neurologist', _('Neurologist')),
        ('obstetrician', _('Obstetrician')),
        ('ophthalmologist', _('Ophthalmologist')),
        ('pediatrician', _('Pediatrician')),
        ('psychiatrist', _('Psychiatrist')),
        ('surgeon', _('Surgeon')),
        ('other', _('Other')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='doctor_profile',
        limit_choices_to={'user_type': 'doctor'}
    )
    specialization = models.CharField(
        _('Specialization'), 
        max_length=50, 
        choices=SPECIALIZATION_CHOICES
    )
    license_number = models.CharField(_('License Number'), max_length=50, unique=True)
    biography = models.TextField(_('Biography'), blank=True)
    years_of_experience = models.PositiveIntegerField(
        _('Years of Experience'), 
        default=0,
        validators=[MaxValueValidator(70)]
    )
    accepting_new_patients = models.BooleanField(_('Accepting New Patients'), default=True)
    
    class Meta:
        verbose_name = _('Doctor')
        verbose_name_plural = _('Doctors')
        ordering = ['user__last_name', 'user__first_name']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['specialization']),
        ]
    
    def __str__(self):
        return f"Dr. {self.user.get_full_name()} ({self.get_specialization_display()})"
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('doctor-detail', args=[str(self.id)])
    
    @property
    def name(self):
        return f"Dr. {self.user.get_full_name()}"
    
    @property
    def full_name(self):
        return self.user.get_full_name()


class DiagnosisHistory(models.Model):
    """
    Model representing a patient's health metrics recorded over time.
    Each record is for a specific month and year.
    """
    LEVEL_CHOICES = [
        ('normal', _('Normal')),
        ('lower_than_average', _('Lower than Average')),
        ('higher_than_average', _('Higher than Average')),
        ('critical_low', _('Critical Low')),
        ('critical_high', _('Critical High')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(
        Patient, 
        on_delete=models.CASCADE,
        related_name='diagnosis_histories',
        verbose_name=_('Patient')
    )
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.SET_NULL,
        related_name='diagnosis_histories',
        verbose_name=_('Doctor'),
        null=True,
        blank=True
    )
    month = models.CharField(_('Month'), max_length=10)
    year = models.PositiveIntegerField(
        _('Year'),
        validators=[MinValueValidator(1900), MaxValueValidator(2100)]
    )
    
    # Blood pressure - systolic
    blood_pressure_systolic_value = models.PositiveIntegerField(
        _('Systolic Blood Pressure Value'),
        validators=[MinValueValidator(50), MaxValueValidator(250)]
    )
    blood_pressure_systolic_levels = models.CharField(
        _('Systolic Blood Pressure Levels'),
        max_length=25,
        choices=LEVEL_CHOICES,
        default='normal'
    )
    
    # Blood pressure - diastolic
    blood_pressure_diastolic_value = models.PositiveIntegerField(
        _('Diastolic Blood Pressure Value'),
        validators=[MinValueValidator(30), MaxValueValidator(150)]
    )
    blood_pressure_diastolic_levels = models.CharField(
        _('Diastolic Blood Pressure Levels'),
        max_length=25,
        choices=LEVEL_CHOICES,
        default='normal'
    )
    
    # Heart rate
    heart_rate_value = models.PositiveIntegerField(
        _('Heart Rate Value'),
        validators=[MinValueValidator(30), MaxValueValidator(220)]
    )
    heart_rate_levels = models.CharField(
        _('Heart Rate Levels'),
        max_length=25,
        choices=LEVEL_CHOICES,
        default='normal'
    )
    
    # Respiratory rate
    respiratory_rate_value = models.PositiveIntegerField(
        _('Respiratory Rate Value'),
        validators=[MinValueValidator(5), MaxValueValidator(60)]
    )
    respiratory_rate_levels = models.CharField(
        _('Respiratory Rate Levels'),
        max_length=25,
        choices=LEVEL_CHOICES,
        default='normal'
    )
    
    # Temperature
    temperature_value = models.FloatField(
        _('Temperature Value'),
        validators=[MinValueValidator(95.0), MaxValueValidator(108.0)]
    )
    temperature_levels = models.CharField(
        _('Temperature Levels'),
        max_length=25,
        choices=LEVEL_CHOICES,
        default='normal'
    )
    
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Diagnosis History')
        verbose_name_plural = _('Diagnosis Histories')
        ordering = ['-year', '-month']
        indexes = [
            models.Index(fields=['patient', '-year', '-month']),
            models.Index(fields=['doctor']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['patient', 'month', 'year'],
                name='unique_patient_diagnosis_history'
            )
        ]
    
    def __str__(self):
        return f"{self.patient.name} - {self.month} {self.year}"


class DiagnosticList(models.Model):
    """
    Model representing diagnosed conditions for a patient.
    """
    STATUS_CHOICES = [
        ('active', _('Actively being treated')),
        ('controlled', _('Controlled')),
        ('resolved', _('Resolved')),
        ('monitoring', _('Monitoring')),
        ('chronic', _('Chronic')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(
        Patient, 
        on_delete=models.CASCADE,
        related_name='diagnostics',
        verbose_name=_('Patient')
    )
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.SET_NULL,
        related_name='diagnostics',
        verbose_name=_('Doctor'),
        null=True,
        blank=True
    )
    name = models.CharField(_('Diagnosis Name'), max_length=255)
    description = models.TextField(_('Description'), blank=True)
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    diagnosed_date = models.DateField(_('Diagnosed Date'), null=True, blank=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Diagnostic')
        verbose_name_plural = _('Diagnostics')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['patient', 'name']),
            models.Index(fields=['doctor']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.patient.name} - {self.name} ({self.get_status_display()})"


class LabResult(models.Model):
    """
    Model representing laboratory test results for a patient.
    """
    RESULT_STATUS_CHOICES = [
        ('normal', _('Normal')),
        ('abnormal', _('Abnormal')),
        ('critical', _('Critical')),
        ('pending', _('Pending')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(
        Patient, 
        on_delete=models.CASCADE,
        related_name='lab_results',
        verbose_name=_('Patient')
    )
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.SET_NULL,
        related_name='lab_results',
        verbose_name=_('Doctor'),
        null=True,
        blank=True
    )
    name = models.CharField(_('Test Name'), max_length=255)
    result_value = models.CharField(_('Result Value'), max_length=255, blank=True)
    result_unit = models.CharField(_('Result Unit'), max_length=50, blank=True)
    reference_range = models.CharField(_('Reference Range'), max_length=255, blank=True)
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=RESULT_STATUS_CHOICES,
        default='pending'
    )
    performed_date = models.DateField(_('Performed Date'))
    reported_date = models.DateField(_('Reported Date'), null=True, blank=True)
    notes = models.TextField(_('Notes'), blank=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Lab Result')
        verbose_name_plural = _('Lab Results')
        ordering = ['-performed_date']
        indexes = [
            models.Index(fields=['patient', '-performed_date']),
            models.Index(fields=['doctor']),
            models.Index(fields=['name']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.patient.name} - {self.name} ({self.performed_date})"


class Appointment(models.Model):
    """
    Model representing appointments between patients and doctors
    """
    STATUS_CHOICES = [
        ('scheduled', _('Scheduled')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
        ('no_show', _('No Show')),
        ('rescheduled', _('Rescheduled')),
    ]
    
    APPOINTMENT_TYPE_CHOICES = [
        ('check_up', _('Regular Check-up')),
        ('follow_up', _('Follow-up Visit')),
        ('consultation', _('Consultation')),
        ('emergency', _('Emergency')),
        ('procedure', _('Medical Procedure')),
        ('lab_work', _('Laboratory Work')),
        ('other', _('Other')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name=_('Patient')
    )
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name=_('Doctor')
    )
    appointment_date = models.DateField(_('Appointment Date'))
    appointment_time = models.TimeField(_('Appointment Time'))
    appointment_type = models.CharField(
        _('Appointment Type'),
        max_length=20,
        choices=APPOINTMENT_TYPE_CHOICES,
        default='check_up'
    )
    reason = models.TextField(_('Reason for Visit'), blank=True)
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='scheduled'
    )
    notes = models.TextField(_('Notes'), blank=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Appointment')
        verbose_name_plural = _('Appointments')
        ordering = ['-appointment_date', '-appointment_time']
        indexes = [
            models.Index(fields=['patient', '-appointment_date']),
            models.Index(fields=['doctor', '-appointment_date']),
            models.Index(fields=['status']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['doctor', 'appointment_date', 'appointment_time'],
                name='unique_doctor_appointment_slot'
            )
        ]
    
    def __str__(self):
        return f"{self.patient.name} with {self.doctor.name} on {self.appointment_date} at {self.appointment_time}"