from django import forms
from .models import Regestration

class Form_Registration(forms.ModelForm):
    class Meta:
        model = Regestration
        fields = "__all__"

class Form_login(forms.ModelForm):
    class Meta:
        model = Regestration
        fields = ['email','password']