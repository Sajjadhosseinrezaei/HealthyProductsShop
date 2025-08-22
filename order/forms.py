from django import forms
from django.utils.translation import gettext_lazy as _

class SalesReportForm(forms.Form):
    start_date = forms.DateField(
        label=_("تاریخ شروع"),
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=True
    )
    end_date = forms.DateField(
        label=_("تاریخ پایان"),
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=True
    )