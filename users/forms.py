"""
BloodConnect User Forms
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, EmergencyContact


class UserRegistrationForm(UserCreationForm):
    role = forms.ChoiceField(choices=[
        ('donor', 'Blood Donor'),
        ('seeker', 'Blood Seeker'),
        ('hospital', 'Hospital'),
    ], widget=forms.RadioSelect, label='Register As')
    
    first_name = forms.CharField(max_length=50, required=False, label='First Name')
    last_name = forms.CharField(max_length=50, required=False, label='Last Name')
    email = forms.EmailField(required=False)
    phone_number = forms.CharField(max_length=15, required=False)
    address = forms.CharField(widget=forms.Textarea(attrs={"rows": 3}), required=False)
    city = forms.CharField(max_length=100, required=False)
    state = forms.CharField(max_length=100, required=False)
    
    # Hospital specific fields (optional by default, validated conditionally)
    hospital_name = forms.CharField(max_length=200, required=False, label='Hospital Name')
    hospital_type = forms.ChoiceField(choices=[
        ('government', 'Government'),
        ('private', 'Private'),
        ('trust', 'Trust / NGO'),
        ('semi-govt', 'Semi-Government'),
    ], required=False, label='Hospital Type')
    registration_number = forms.CharField(max_length=50, required=False, label='Registration/License Number')
    emergency_contact = forms.CharField(max_length=15, required=False, label='Emergency Contact Number')
    blood_bank_available = forms.BooleanField(required=False, initial=True, label='Blood Bank Available')
    website = forms.URLField(required=False, label='Website URL')
    verification_document = forms.FileField(
        required=False,
        label='Upload Verification Document (PDF only)',
        widget=forms.FileInput(attrs={'accept': '.pdf'})
    )
    latitude = forms.DecimalField(max_digits=9, decimal_places=6, required=False, widget=forms.HiddenInput())
    longitude = forms.DecimalField(max_digits=9, decimal_places=6, required=False, widget=forms.HiddenInput())
    
    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_number',
                  'address', 'city', 'state', 'role', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, (forms.RadioSelect, forms.CheckboxInput, forms.HiddenInput)):
                field.widget.attrs.update({'class': 'form-control'})
        
        if 'hospital_name' in self.fields:
            self.fields['hospital_name'].widget.attrs['placeholder'] = 'e.g. City General Mumbai Hospital'
        
        if 'username' in self.fields:
            self.fields['username'].max_length = 40
            self.fields['username'].widget.attrs['maxlength'] = 40
            self.fields['username'].help_text = 'Required. 40 characters or fewer. Lowercase letters, digits and @/_/- only. (Recommended: start with a special character).'
        if 'password1' in self.fields:
            self.fields['password1'].help_text = 'Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, one number, and one special character (e.g. @$!%*?&#).'

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            if len(username) > 40:
                raise forms.ValidationError('Username must be 40 characters or fewer.')
            if any(char.isupper() for char in username):
                raise forms.ValidationError('Username must contain lowercase letters only (no capital letters allowed).')
            import re
            if not re.match(r'^[a-z0-9@_\-]+$', username):
                raise forms.ValidationError('Username can only contain lowercase letters, digits, and @/_/- characters.')
        return username

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if password:
            import re
            if len(password) < 8:
                raise forms.ValidationError('Password must be at least 8 characters long.')
            if not re.search(r'[A-Z]', password):
                raise forms.ValidationError('Password must contain at least one uppercase letter.')
            if not re.search(r'[a-z]', password):
                raise forms.ValidationError('Password must contain at least one lowercase letter.')
            if not re.search(r'[0-9]', password):
                raise forms.ValidationError('Password must contain at least one number.')
            if not re.search(r'[@$!%*?&#]', password):
                raise forms.ValidationError('Password must contain at least one special character (e.g. @$!%*?&#).')
        return password

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        
        # Validation based on role
        if role == 'hospital':
            hospital_name = cleaned_data.get('hospital_name')
            if not hospital_name:
                self.add_error('hospital_name', 'Hospital Name is required.')
            
            hospital_type = cleaned_data.get('hospital_type')
            if not hospital_type:
                self.add_error('hospital_type', 'Hospital Type is required.')
            
            registration_number = cleaned_data.get('registration_number')
            if not registration_number:
                self.add_error('registration_number', 'Registration/License Number is required.')
                
            first_name = cleaned_data.get('first_name')
            if not first_name:
                self.add_error('first_name', 'Contact Person Name is required.')
                
            last_name = cleaned_data.get('last_name')
            if not last_name:
                self.add_error('last_name', 'Designation is required.')
                
            phone_number = cleaned_data.get('phone_number')
            if not phone_number:
                self.add_error('phone_number', 'Contact Number is required.')
                
            address = cleaned_data.get('address')
            if not address:
                self.add_error('address', 'Address is required.')
                
            city = cleaned_data.get('city')
            if not city:
                self.add_error('city', 'City is required.')
                
            state = cleaned_data.get('state')
            if not state:
                self.add_error('state', 'State is required.')
                
            verification_document = cleaned_data.get('verification_document')
            if verification_document:
                if not verification_document.name.lower().endswith('.pdf'):
                    self.add_error('verification_document', 'Only PDF files are allowed for the verification document.')
        else:
            # Donor or Seeker
            first_name = cleaned_data.get('first_name')
            if not first_name:
                self.add_error('first_name', 'First Name is required.')
            
            last_name = cleaned_data.get('last_name')
            if not last_name:
                self.add_error('last_name', 'Last Name is required.')
                
            phone_number = cleaned_data.get('phone_number')
            if not phone_number:
                self.add_error('phone_number', 'Phone Number is required.')
                
        return cleaned_data


class CustomLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone_number',
                  'secondary_phone', 'address', 'city', 'state', 'pincode',
                  'aadhar_card_number', 'profile_picture']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class EmergencyContactForm(forms.ModelForm):
    class Meta:
        model = EmergencyContact
        fields = ['name', 'phone_number', 'secondary_phone', 'relationship', 'address', 'email']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
