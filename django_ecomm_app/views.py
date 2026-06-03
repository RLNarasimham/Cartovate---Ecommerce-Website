from django.shortcuts import render,get_object_or_404,redirect
from django_ecomm_app.models import Order,OrderItem,Product,Category,CartItem,Cart,Wishlist
from django.db.models import Q
from django_ecomm_app.forms import CheckoutForm, RegisterForm
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import F
from django.db import transaction
from django.contrib.auth.decorators import login_required

# Create your views here.
# ── HOME PAGE ─────────────────────────────────────────────────────────
def show_home_view(request):
    query=request.GET.get('q','')
    categories=Category.objects.all()
    products=Product.objects.filter(pr_stock__gt=0)
    category=request.GET.get('pr_category')

    if query:
        products=products.filter(
            Q(pr_name__icontains=query) | Q(pr_description__icontains=query)
        )
    
    if category:
        products=products.filter(pr_category__cat_name=category)

    paginator=Paginator(products,5)
    page_num=request.GET.get('page',1)
    page_obj=paginator.get_page(page_num)


    return render(request,'django_ecomm_app/homepage.html',{
        'products':products,
        'categories':categories,
        'query':query,
        'selected_category': category,
        'page_obj':page_obj
    })

# ── PRODUCT DETAIL ────────────────────────────────────────────────────
def product_detail_view(request,pk):
    product=get_object_or_404(Product,pk=pk)
    in_wishlist=False
    if request.user.is_authenticated:
        in_wishlist=Wishlist.objects.filter(user=request.user,product=product).exists()
    return render(request,'django_ecomm_app/product_details.html',{'product':product,'in_wishlist':in_wishlist})


# ── REGISTER ──────────────────────────────────────────────────────────
def register_view(request):
    if request.method=='POST':
        form=RegisterForm(request.POST)
        if form.is_valid():
            user=form.save()
            login(request,user)
            messages.success(request,'Welcome to E-commerce website!!!')
            return redirect('home')
    else:
        form=RegisterForm()
    return render(request,'django_ecomm_app/register.html',{'form':form})


# ── LOGIN ─────────────────────────────────────────────────────────────
def login_view(request):
    if request.method=='POST':
        username=request.POST['username']
        password=request.POST['password']
        user=authenticate(request,username=username,password=password)
        if user:
            login(request,user)
            return redirect('home')
        messages.error(request,'invalid username or password')
    return render(request,'django_ecomm_app/login.html')

# ── LOGOUT ────────────────────────────────────────────────────────────
def logout_view(request):
    logout(request)
    return redirect('home')

# ── CART ──────────────────────────────────────────────────────────────
@login_required
def show_cart_view(request):
    cart,_=Cart.objects.get_or_create(user=request.user)
    return render(request,'django_ecomm_app/cart.html',{'cart':cart})

@login_required
def add_to_cart_view(request,pk):
    product=get_object_or_404(Product,pk=pk)
    cart, _=Cart.objects.get_or_create(user=request.user)
    item,created=CartItem.objects.get_or_create(cart=cart,cart_product=product)
    if not created:
        item.cart_quantity+=1
        item.save()
    messages.success(request,f'{product.pr_name} added to cart!')
    return redirect('cart')

@login_required
def remove_from_cart_view(request,pk):
    item=get_object_or_404(CartItem,pk=pk,cart__user=request.user)
    item.delete()
    return redirect('cart')

@login_required
def update_cart_qty_view(request,pk):
    item=get_object_or_404(CartItem,pk=pk,cart__user=request.user)
    raw_q = request.POST.get('quantity', None)
    if raw_q is None:
        raw_q = request.POST.get('cart_quantity', None)
    try:
        quantity = int(raw_q) if raw_q is not None else 1
    except (ValueError, TypeError):
        quantity = 1

    if quantity > 0:
        item.cart_quantity = quantity
        item.save()
    else:
        item.delete()

    return redirect('cart')

# ── ORDERS ────────────────────────────────────────────────────────────
@login_required
def place_order_view(request):
    cart = get_object_or_404(Cart, user=request.user)
    
    if not cart.cartitem_set.exists():
        messages.error(request, 'Your cart is empty')
        return redirect('cart')
        
    # 1. MOVED UP: Pre-check stock for BOTH GET and POST requests
    # If they click "Proceed to Checkout" with 100 items, this instantly kicks them back.
    for item in cart.cartitem_set.all():
        if item.cart_product.pr_stock < item.cart_quantity:
            messages.error(
                request, 
                f"Sorry, we only have {item.cart_product.pr_stock} of '{item.cart_product.pr_name}' left in stock. Please update your quantity."
            )
            return redirect('cart')
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    order = Order.objects.create(
                        user=request.user,
                        ord_total_price=cart.total(),
                        ord_shipping_address=form.cleaned_data['shipping_address']
                    )
                    
                    for item in cart.cartitem_set.all():
                        # Double-check inside the transaction just in case someone else 
                        # bought the last item while this user was typing their address
                        item.cart_product.refresh_from_db()
                        
                        if item.cart_product.pr_stock < item.cart_quantity:
                            # If stock ran out while they were typing, trigger an error
                            raise ValueError(f"Sorry, '{item.cart_product.pr_name}' just went out of stock!")

                        OrderItem.objects.create(
                            order=order,
                            product=item.cart_product,
                            quantity=item.cart_quantity,
                            price=item.cart_product.pr_price
                        )
                        
                        item.cart_product.pr_stock = F('pr_stock') - item.cart_quantity
                        item.cart_product.save()
                        
                    cart.cartitem_set.all().delete()
                
                messages.success(request, f'Order #{order.id} placed successfully!')
                return redirect('my_orders')
                
            except ValueError as e:
                # Catches the specific stock error if it changed during checkout
                messages.error(request, str(e))
                return redirect('cart')
                
            except Exception as e:
                messages.error(request, "An error occurred while processing your order. Please try again.")
                return redirect('cart')
                
    else:
        form = CheckoutForm()
        
    return render(request, 'django_ecomm_app/place_order.html', {'cart': cart, 'form': form})

@login_required
def my_orders_view(request):
    orders=Order.objects.filter(user=request.user).order_by('-ord_created_at')
    return render(request,'django_ecomm_app/my_orders.html',{'orders':orders})

# ── WISHLIST ────────────────────────────────────────────────────────────
@login_required
def toggle_wishlist_view(request,pk):
    product=get_object_or_404(Product,pk=pk)
    obj,created=Wishlist.objects.get_or_create(user=request.user,product=product)
    if not created:
        obj.delete()
        messages.info(request,'Product Deleted from Wishlist!')
    else:
        messages.success(request,'Product Added to Wishlist!')
    next_url = request.GET.get('next')
    if next_url:
        return redirect(next_url)
    return redirect('product_detail',pk=pk)


@login_required
def wishlist_view(request):
    items = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'django_ecomm_app/wishlist.html', {'items': items})