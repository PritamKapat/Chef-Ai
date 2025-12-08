
from django.urls import path
from . import views
from .views import generate_recipe


urlpatterns = [
    path('',views.signup,name='signup'),
    path('login/',views.user_login,name='login'),
    path("inventory/", views.inventory_page, name="inventory"),
    path("inventory/add/", views.add_inventory, name="add_inventory"),
    path("inventory/edit/", views.edit_inventory, name="edit_inventory"),
    path("inventory/delete/", views.delete_inventory, name="delete_inventory"),
    path("deduct_inventory/", views.deduct_inventory, name="deduct_inventory"),
    path('logout/',views.LogoutPage,name='logout'),
    path('home/',views.home, name='index-page'),
    path('generate/',views.generate,name="generate-page"),
    path('wishlist/',views.wishlist,name="wishlist-page"),
    path('generate-recipe/', generate_recipe, name='generate_recipe'),
    path('add-to-wishlist/', views.add_to_wishlist, name='add_to_wishlist'),
    path('delete/<int:id>/', views.delete_item, name='delete-page'),
    path('update/<int:id>',views.update, name="update-page"),
    path('profile/',views.profile, name="profile-page"),
    path('ai-scan-predict/', views.ai_scan_predict, name='ai_scan_predict'),
    path("generate_recipe_image/", views.generate_recipe_image, name="generate_recipe_image"),

]
