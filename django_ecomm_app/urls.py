from django.urls import path
from django_ecomm_app import views
from django.contrib.auth import views as auth_views

urlpatterns=[
    path('',views.show_home_view,name='home'),
    path('product/<int:pk>/',views.product_detail_view,name='product_detail'),
    path('register/',views.register_view,name='register'),
    path('login/',views.login_view,name='login'),
    path('logout/',views.logout_view,name='logout'),
    path('cart/',views.show_cart_view,name='cart'),
    path('wishlist/',views.wishlist_view,name='wishlist'),
    path('toggle_wishlist/<int:pk>/',views.toggle_wishlist_view,name='toggle_wishlist'),
    path('upd_cart/<int:pk>/',views.update_cart_qty_view,name='update_cart'),
    path('cart/add/<int:pk>/',views.add_to_cart_view,name='add to cart'),
    path('cart/delete/<int:pk>/',views.remove_from_cart_view,name='delete from cart'),
    path('checkout/',views.place_order_view,name='checkout'),
    path('my_orders/',views.my_orders_view,name='my_orders'),

    #Password reset routes
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='django_ecomm_app/password_reset.html',
        email_template_name='django_ecomm_app/password_reset_email.html',
        subject_template_name='django_ecomm_app/password_reset_subject.txt',
        success_url='/password_reset/done/'
    ), name='password_reset'),
    
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='django_ecomm_app/password_reset_done.html'
    ), name='password_reset_done'),
    
    path('password_reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='django_ecomm_app/password_reset_confirm.html',
        success_url='/password_reset/complete/'
    ), name='password_reset_confirm'),
    
    path('password_reset/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='django_ecomm_app/password_reset_complete.html'
    ), name='password_reset_complete')
]