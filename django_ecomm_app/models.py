from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Category(models.Model):
    cat_name=models.CharField(max_length=150)
    cat_image=models.ImageField(upload_to='categories/',blank=True,null=True)

    def __str__(self):
        return self.cat_name
    
    class Meta:
        verbose_name_plural='Categories'


class Product(models.Model):
    pr_name=models.CharField(max_length=150,verbose_name='Product Name')
    pr_description=models.TextField(blank=True,verbose_name='Product Description')
    pr_price=models.DecimalField(max_digits=6,decimal_places=2,verbose_name="Product's Price")
    pr_old_price=models.DecimalField(max_digits=8,decimal_places=2,verbose_name="Product's Old Price")
    pr_stock=models.PositiveIntegerField(default=0,verbose_name='Product Stock')
    pr_category=models.ForeignKey(Category,on_delete=models.SET_NULL,null=True,related_name='products',verbose_name="Product's Category")
    pr_image=models.ImageField(upload_to='products/',blank=True,null=True,verbose_name="Product's Image")
    is_featured=models.BooleanField(default=False)
    pr_created_at=models.DateTimeField(auto_now_add=True,verbose_name="Product's Creation Date")
    pr_rating=models.DecimalField(max_digits=2,decimal_places=1,default=0.0)

    def __str__(self):
        return self.pr_name
    
    def discount_percent(self):
        if self.pr_old_price:
            return int((1-self.pr_price/self.pr_old_price)*100)
        return 0


class Cart(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    cart_created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Cart"
    
    def total(self):
        return sum(item.subtotal() for item in self.cartitem_set.all())
    

class CartItem(models.Model):
    cart=models.ForeignKey(Cart,on_delete=models.CASCADE)
    cart_product=models.ForeignKey(Product,on_delete=models.CASCADE)
    cart_quantity=models.PositiveIntegerField(default=1)

    def subtotal(self):
        return self.cart_product.pr_price * self.cart_quantity

class Order(models.Model):
    STATUS=[
        ('pending','Pending'),
        ('confirmed','Confirmed'),
        ('shipped','Shipped'),
        ('delivered','Delivered'),
    ]
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    ord_total_price=models.DecimalField(max_digits=10,decimal_places=2,verbose_name="Order's Total Price")
    ord_status=models.CharField(max_length=20,choices=STATUS,default='pending',verbose_name="Order's Status")
    ord_shipping_address=models.TextField(verbose_name="Order's Shipping Address")
    ord_created_at=models.DateTimeField(auto_now_add=True,verbose_name="Order's Creation Date")

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"
    

class OrderItem(models.Model):
    order=models.ForeignKey(Order,on_delete=models.CASCADE,related_name='items')
    product=models.ForeignKey(Product,on_delete=models.PROTECT)
    quantity=models.PositiveIntegerField()
    price=models.DecimalField(max_digits=10,decimal_places=2)

class Wishlist(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)

    class Meta:
        unique_together=('user','product')