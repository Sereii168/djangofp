from django import forms
from .models import *
from inventory.models import *
from django.forms import formset_factory

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ('name','phone','address','email','gstn')


class SelectSupplierForm(forms.ModelForm):
    def __init__(self, *args, **kwarge):
        super().__init__(*args,**kwarge)
        self.fields['supplier'].queryset = Supplier.objects.filter(is_deleted  = False)
        self.fields['supplier'].widget.attrs.update({'class':'textinput form-control'})

    class Meta:
        model = PurchaseBill
        fields = ['supplier']

class PurchaseItemForm(forms.ModelForm):
    def __init__(self,*args,**kwarge):
        super().__init__(*args,**kwarge)
        self.fields['stock'].queryset = Stock.objects.filter(is_deleted = False)
        self.fields['stock'].widget.attrs.update({'class':'textinput form-control setprice stock','required':'true'})
        self.fields['quantity'].widget.attrs.update({'class':'textinput form-control setprice quantity','min':'1','required': 'true'})
        self.fields['perprice'].widget.attrs.update({'class':'textinput form-control setprice price','min':'1','required': 'true'})

    class Meta:
        model = PurchaseItem
        fields = ['stock','quantity','perprice']

PurchaseItemFormset = formset_factory(PurchaseItemForm, extra=1)


class PurchaseDetailsForm(forms.ModelForm):
    class Meta:
        model = PurchaseBillDetails
        fields = ('eway', 'veh', 'destination', 'po', 'cgst', 'igst', 'cess', 'tcs', 'total', )
