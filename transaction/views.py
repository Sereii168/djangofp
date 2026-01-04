from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from.models import *
from .forms import *


class CreateSupplier(SuccessMessageMixin, generic.CreateView):
    model = Supplier
    form_class = SupplierForm
    success_message = 'Create Supplier Successfully..'
    success_url = '/transaction/supplier_list'
    template_name = 'supplier/create_supplier.html'


class SupplierList(generic.ListView):
    model = Supplier
    queryset = Supplier.objects.filter(is_deleted = False)
    template_name = 'supplier/suppliers_List.html'
    context_object_name = 'supplier'
    paginate_by = 10


class UpdateSupplier(SuccessMessageMixin, generic.CreateView):
    model = Supplier
    form_class = SupplierForm
    success_message = 'Update Supplier Successfully..'
    success_url = '/inventory/supplier-list'
    template_name = 'supplier/update_supplier.html'

class DeleteSupplier(generic.View):
    template_name = 'supplier/delete_supplier.html'
    success_message = 'Delete Successfully...'

    def get(self,request,pk):
        sup = get_object_or_404(Supplier,pk=pk)
        return render(request,self.template_name,{'sup':sup})
    def post(self,request,pk):
        sup = get_object_or_404(Supplier,pk=pk)
        sup.is_deleted = True
        sup.save()
        messages.success(request,self.success_message)
        return redirect('supplier_list')
    


class PurchaseView(generic.ListView):
    model = PurchaseBill
    template_name = 'purchase/purchase_list.html'
    context_object_name = 'bills'
    ordering = ['-time']
    paginate_by = 10


class SelectSupplierView(generic.View):
    form_class = SelectSupplierForm
    template_name = 'purchase/select_supplier.html'

    def get(self,request,*args,**kwargs):
        form = self.form_class
        return render(request,self.template_name,{'form':form})
    
    def post(self,request,*args,**kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            supplierid = request.POST.get('supplier')
            supplier = get_object_or_404(Supplier,id=supplierid)
            return redirect('new_purchase',supplier.id)
        return render(request,self.template_name,{'form':form})
    
class PurchaseCreateView(generic.View):
    template_name = 'purchase/new_purchase.html'

    def get(self,request,pk):
        formset = PurchaseItemFormset(request.GET or None)
        supplierobj = get_object_or_404(Supplier, pk =pk)
        context ={
            'formset' : formset,
            'supplier' : supplierobj,
        }
        return render(request,self.template_name,context)
    
    def post(self,request,pk):
        formset = PurchaseItemFormset(request.POST)
        supplierobj = get_object_or_404(Supplier,pk=pk)
        if formset.is_valid():
                # save bill
                billobj = PurchaseBill(supplier=supplierobj)
                billobj.save()
                # save bill details
                billdetailsobj = PurchaseBillDetails(billno=billobj)
                billdetailsobj.save()
                for form in formset:
                    billitem = form.save(commit=False)
                    billitem.billno = billobj
                    stock = get_object_or_404(Stock,name=billitem.stock.name)
                    billitem.totalprice = billitem.perprice * billitem.quantity
                    stock.quantity += billitem.quantity
                    stock.save()
                    billitem.save()
                messages.success(request,"Purchased items have been registered successfully")
                return redirect('purchase_bill',billno=billobj.billno)
                # return redirect("/")
        formset = PurchaseItemFormset(request.GET or None)
        context = {
        'formset' : formset,
        'supplier' : supplierobj
    } 
        return render(request, self.template_name, context)



class PurchaseDeleteView(SuccessMessageMixin,generic.DeleteView):
    model = PurchaseBill
    template_name = 'purchase/purchase_delete.html'
    success_url = '/transactions/purchases'

    def delete(self,*args,**kwargs):
        self.object = self.get_object()
        items = PurchaseBill.objects.filter(billno = self.object.billno)
        for item in items:
            stock = get_object_or_404(Stock,name = item.stock.name)
            if stock.is_deleted == False:
                stock.quantity -= item.quantity
                stock.save()
        messages.success(self.request, "Purchase bill has been deleted successfully")
        return super(PurchaseDeleteView,self).delete(*args,**kwargs)


class PurchaseBillView(generic.View):
    model = PurchaseBill
    template_name = "bill/purchase_bill.html"
    bill_base = "bill/bill_base.html"
    form_class = PurchaseDetailsForm

    def get_bill_context(self, billno,form):
        bill = get_object_or_404(PurchaseBill, billno = billno)
        items = PurchaseItem.objects.filter(billno = billno)
        billdetails = get_object_or_404(PurchaseBillDetails , billno = billno)
        return{
            'bill' : bill,
            'item' : items,
            'billdetails' : billdetails,
            'bill_base' : self.bill_base,
            'form' : form
        }
    def get(self, request , billno):
        billdetailobj = get_object_or_404(PurchaseBillDetails, billno = billno)
        form = self.form_class(instance=billdetailobj)
        context = self.get_bill_context(billno,form)
        return render(request,self.template_name ,context)
    
    def post(self, request , billno):
        billdetailobj = get_object_or_404(PurchaseBillDetails, billno = billno)
        form = self.form_class(request.POST, instance=billdetailobj)

        if form.is_valaid():
            form.save()
            messages.success(request,'Bill Details has been modified successfully')
        else:
            messages.error(request,'There was an error updating the bill details. Please check the form.')

        context = self.get_bill_context(billno,form)
        return render(request, self.template_name, context)
        

    