from .models import Order, Customer
from django import forms
from django.contrib.auth.models import User
from django.forms import  TextInput, EmailInput, PasswordInput

class CheckoutForm(forms.ModelForm):
    
    class Meta:
        model = Order
        fields = ['ordered_by', 'shipping_address', 'mobile', 'email','payment_method']
        widgets = {
            'ordered_by': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',
                'placeholder': 'Ordered By'
                }),
            'shipping_address': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',
                'placeholder': 'Shipping Address'
                }),
            'mobile': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',
                'placeholder': 'Mobile'
                }),
            'email': EmailInput(attrs={
                'class': "form-control", 
                'style': 'max-width: 300px;',
                'placeholder': 'Email'
                })
        }
    
class CustomerRegistrationForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',
                'placeholder': 'Name'
                }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',
                'placeholder': 'password'
                }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
                'class': "form-control", 
                'style': 'max-width: 300px;',
                'placeholder': 'Email'
                }))

    class Meta:
        model = Customer
        fields = ["username", "password", "email", "full_name", "address"]
        widgets = {
            'full_name': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',
                'placeholder': 'Full Name'
                }),
            'address': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',
                'placeholder': 'Address'
                }),
            
        }

    def clean_username(self):
        uname = self.cleaned_data.get("username")
        if User.objects.filter(username=uname).exists():
            raise forms.ValidationError(
                "Customer with this username already exists.")

        return uname
    
class CustomerLoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput())
    password = forms.CharField(widget=forms.PasswordInput())
    
    
class AdminLoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput())
    password = forms.CharField(widget=forms.PasswordInput())
    