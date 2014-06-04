from django import forms
#from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist


User = get_user_model()

    
def phoneCleaner(phone_no):
    prefix = ['07','08','09']
    if phone_no.isdigit() and len(phone_no)==11:
        if phone_no[0:2] in prefix:
            return True
        return False


class RegisterForm(forms.Form): 
        phone_no = forms.CharField(min_length=11, max_length=11)#enforce min and max on flex and generate all values dynamically with at least empty string
        email = forms.EmailField(required=False)
        confirm_email = forms.EmailField(required=False)

        def clean_phone_no(self):
                phone_no = self.cleaned_data['phone_no']
                if not phoneCleaner(phone_no):
                    raise forms.ValidationError("Please check the format of your Phone number")

                try:
                    User.objects.get(phone_no__iexact=phone_no)
                except User.DoesNotExist:
                    return phone_no

                raise forms.ValidationError("Phone number already exists")

        def clean(self):
                cleaned_data = super(RegisterForm, self).clean()
                email = cleaned_data.get('email')
                confirm_email = cleaned_data.get('confirm_email')

                if email != confirm_email:
                    raise forms.ValidationError("Email addresses did not correspond")

                try:
                    User.objects.get(email=email)
                except:
                    return cleaned_data

                raise forms.ValidationError("Email already exists")
                
        def save(self, form_data):
                user = User.objects.create_user(form_data['phone_no'],form_data['email'])
                reset_password = User.objects.make_random_password(length=10, allowed_chars='abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789')
                user.set_password(reset_password)
                user.is_active = True
                user.save()
                return user
        
                
                
class ChangePasswordForm(forms.Form):
        old_password = forms.CharField(min_length=4, max_length=20)
        new_password = forms.CharField(min_length=4, max_length=20)
        confirm_password = forms.CharField(min_length=4, max_length=20)

        def clean(self):
            cleaned_data = super(ChangePasswordForm, self).clean()
            new_password = cleaned_data.get('new_password')
            confirm_password = cleaned_data.get('confirm_password')
            if new_password != confirm_password:
                    raise forms.ValidationError("Passwords did not match")

            return cleaned_data



class ForgetPasswordForm(forms.Form):
    phone_no = forms.CharField(min_length=11, max_length=11)#the user must have entered email add. before hand if not, IVR service

    def clean_phone_no(self):
        phone_no = self.cleaned_data['phone_no']
        if not phoneCleaner(phone_no):
            raise forms.ValidationError("Please check the format of your Phone number")
        return phone_no



class EditUserForm(forms.Form):
    phone_no = forms.CharField(min_length=11, max_length=11)#enforce min and max on flex and generate all values dynamically with at least empty string
    email = forms.EmailField(required=False)
    confirm_email = forms.EmailField(required=False)
    alias = forms.CharField(required=False, min_length=5, max_length=20)
    location = forms.CharField(required=False)
    birth_day = forms.DateField(required=False)

    def clean(self):
        cleaned_data = super(EditUserForm, self).clean()
        email = cleaned_data.get('email')
        confirm_email = cleaned_data.get('confirm_email')

        if email != confirm_email:
            raise forms.ValidationError("Email addresses did not correspond")

        try:
            User.objects.get(email=email)
        except:
            return cleaned_data

        raise forms.ValidationError("Email already exists")

