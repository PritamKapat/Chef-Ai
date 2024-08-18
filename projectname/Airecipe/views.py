from django.shortcuts import render,redirect
from groq import Groq
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import WishlistItem  # Import the model
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.models import User # this is for sign Up
from django.contrib.auth import authenticate,login,logout
#from django.shortcuts import render, redirect
from django.contrib import messages
#from django.contrib.auth import authenticate, login



# Home view
def home2(request):
    return render(request, "home2.html")

# Generate recipe view
def generate(request):
    return render(request, "generate.html")
def profile(request):
    return render(request, "profile.html")

# Wishlist view
def wishlist(request):
    items = WishlistItem.objects.all()  # Fetch all wishlist items from the database
    return render(request, "wishlist.html", {'students': items})  # Pass items to the template

# Function to generate the recipe using the Groq API
def recip(itemss):
    client = Groq(api_key="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")

    prompt = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": "You are a recipe generator from the given ingredients only."
            },
            {
                "role": "user",
                "content": f"Generate a recipe using the following ingredients: {itemss}"
            }
        ],
    )
    
    recipe = prompt.choices[0].message.content
    return recipe

@csrf_exempt
def generate_recipe(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        items = data.get('items')

        recipe = recip(items)

        return JsonResponse({'recipe': recipe})
    return JsonResponse({'error': 'Invalid request'}, status=400)



@csrf_exempt
def add_to_wishlist(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            items = data.get('items')
            recipe = data.get('recipe')
            
            if not items or not recipe:
                return JsonResponse({'error': 'Missing items or recipe'}, status=400)

            # Save to the database using the correct field names
            WishlistItem.objects.create(items=items, description=recipe)
            return JsonResponse({'success': True})

        except Exception as e:
            print(f"Error adding to wishlist: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)



def delete_item(request, id):
    # Get the item by its ID, or return a 404 if not found
    item = get_object_or_404(WishlistItem, id=id)
    
    # Delete the item from the database
    item.delete()
    
    # Redirect back to the wishlist page after deletion
    return redirect('wishlist-page')

def update(request,id):
    student=WishlistItem.objects.get(id=id)   
    if request.method == "POST":
        #items=request.POST.get('pitems')
        description=request.POST.get('pdescription')

        if description:
            #student.items=items
            student.description=description
            student.save()
            return redirect('wishlist-page')
    else:
        return render(request,"update.html",{'student': student})
    
# def signupPage(request):
#     if request.method=='POST':
#         uname=request.POST.get('txt')
#         email=request.POST.get('Email')
#         pass1=request.POST.get('password1')
#         pass2=request.POST.get('password2')
        
#         if pass1!=pass2 or User.objects.filter(email=email).exists():
            
#             return redirect('signup-page')
#         else:
#          my_user=User.objects.create_user(uname,email,pass1)
#          my_user.save()
        
#         return redirect('index-page')
#     return render (request,'signUpPage.html')



def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        pass1 = request.POST.get('pass')
        print(username, pass1)

        # Hardcoded authentication for a single user
        if username == 'admin' and pass1 == '#admin':
            # Manually log in the user (bypassing the authentication system)
            # You may want to set a session or flag here if needed
            return redirect('index-page')  # Redirect to the index page on success
        else:
            messages.error(request, "Invalid username or password")
            return redirect('login-page')  # Redirect back to login page on failure
    
    return render(request, 'login.html')


def logoutPage(request):
    logout(request)
    return redirect('login-page')