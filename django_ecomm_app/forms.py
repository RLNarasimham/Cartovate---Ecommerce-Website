from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class RegisterForm(UserCreationForm):
    email=forms.EmailField(required=True)

    class Meta:
        model=User
        fields=['username','email','password1','password2']

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for field in self.fields.values():
            field.widget.attrs['class']='form-control'

class CheckoutForm(forms.Form):
    shipping_address=forms.CharField(
        widget=forms.Textarea(attrs={'rows':3,'class':'form-control'}),
        label='Delivery Address'
    )
    