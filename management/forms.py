from django import forms
from django.contrib.auth.models import User


class AddUserForm(forms.Form):
    username = forms.CharField(label='Username', max_length=30)
    password = forms.CharField(widget=forms.PasswordInput(), label='Password', max_length=30)
    confirm_password = forms.CharField(widget=forms.PasswordInput(), label='Confirm password', max_length=30)
    staff = forms.BooleanField(label="Has staff permissions", required=False)

    def check_for_spaces(self):
        username = self.cleaned_data['username']
        if ' ' in username:
            raise forms.ValidationError('Username should not contain any space')
        return username

    def check_password(self):
        if self.cleaned_data['password'] != self.cleaned_data['confirm_password']:
            raise forms.ValidationError('Password do not match')


class EditUserForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput(), label='Password', max_length=30, required=False)
    # password = forms.CharField(widget=forms.PasswordInput(), label='Password', max_length=30, required=False)
    confirm_password = forms.CharField(widget=forms.PasswordInput(), label='Confirm password', max_length=30,
                                       required=False)
    staff = forms.BooleanField(label="", required=False)

    class Meta:
        fields = ['password', 'is_staff']

    def check_password(self):
        if self.cleaned_data['password'] != self.cleaned_data['confirm_password']:
            raise forms.ValidationError('Password do not match')
