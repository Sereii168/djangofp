from django.db import models
import uuid
from inventory.models import *

class Supplier(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name =  models.CharField(max_length=250)
    phone = models.CharField(max_length=250,unique=True)
    address = models.CharField(max_length=250)
    email = models.EmailField(max_length=254, unique=True)
    gstn = models.CharField(max_length=15, unique=True)
    is_deleted = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name
    
class PurchaseItem (models.Model):
    billno = models.ForeignKey("PurchaseBill", on_delete=models.CASCADE, related_name='purchaseitem')
    stock = models.ForeignKey(Stock , on_delete=models.CASCADE, related_name="purchaseitem")  
    quantity = models.IntegerField(default=1)
    perprice = models.IntegerField(default=1)
    totalprice = models.IntegerField(default=1)

    def __str__(self):
        return "Bill no: "+ str(self.billno.billno)+", Item = "+ self.stock.name

class PurchaseBill(models.Model):
    billno = models.UUIDField(primary_key =True,default=uuid.uuid4)
    time = models.DateTimeField(auto_now_add=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='purchasesupplier')

    def __str__(self):
        return "Bill no: " + str(self.billno)
    def get_total_price(self):
        purchaseitems = PurchaseItem.objects.filter(billno = self)
        total = 0 
        for item in purchaseitems :
            total += item.totalprice
        return total
    def get_items_list(self):
        return PurchaseItem.objects.filter(billno = self)
    
    
class PurchaseBillDetails(models.Model):
    billno = models.ForeignKey(PurchaseBill, on_delete= models.CASCADE, related_name="purchasedetailsbillno")
    
    eway = models.CharField(max_length=50 , blank = True, null=True)
    veh = models.CharField(max_length=50,blank = True, null =True)
    destination = models.CharField(max_length=50, blank=True, null=True)
    po = models.CharField(max_length=50, blank=True, null=True)
    cgst = models.CharField(max_length=50, blank=True, null=True)
    igst = models.CharField(max_length=50, blank=True, null=True)
    cess = models.CharField(max_length=50, blank=True, null=True)
    tcs = models.CharField(max_length=50, blank=True, null=True)
    total = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return "Bill no: "+ str(self.billno.billno)
    
    
    