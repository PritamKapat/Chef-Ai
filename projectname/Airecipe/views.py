from django.shortcuts import render,redirect
from groq import Groq
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import WishlistItem  # Import the model
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.models import User # this is for sign Up
from django.contrib.auth import authenticate, login as auth_login, logout
#from django.shortcuts import render, redirect
from django.contrib import messages
#from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required



# Home view
def home(request):
    return render(request, "home2.html")

# Generate recipe view
def generate(request):
    return render(request, "generate.html")
def profile(request):
    return render(request, "profile.html")
# @login_required(login_url='login')

def signup(request):

    if request.method == 'POST':

        uname = request.POST.get('username')

        email = request.POST.get('email')

        pass1 = request.POST.get('password1')

        pass2 = request.POST.get('password2')


        if pass1 != pass2:

            return render(request, 'signup.html', {"error": "Passwords do not match!"})


        if User.objects.filter(username=uname).exists():

            return render(request, 'signup.html', {"error": "Username already exists! Choose another."})


        my_user = User.objects.create_user(username=uname, email=email, password=pass1)

        my_user.save()

        return redirect('login')  # Redirect to the login page after signup


    return render(request, 'signup.html')



def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        pass1 = request.POST.get('password')
        print(f"USERNAME: {username}, PASSWORD: {pass1}")

        # ✅ Temporary hardcoded login check
        if username == 'admin' and pass1 == '#admin':
            return redirect('index-page')  # Replace with your actual homepage URL name
        else:
            return render(request, 'login.html', {"error": "Invalid credentials!"})

        # Original logic (commented for future use)
        # from django.contrib.auth import authenticate, login as auth_login
        # from django.contrib.auth.models import User

        # if not User.objects.filter(username=username).exists():
        #     return render(request, 'login.html', {"error": "No account exists with this username!"})

        # user = authenticate(request, username=username, password=pass1)

        # if user is not None:
        #     auth_login(request, user)
        #     return redirect('index-page')
        # else:
        #     return render(request, 'login.html', {"error": "Incorrect password!"})

    return render(request, 'login.html')




# @login_required(login_url='login')
def LogoutPage(request):
    logout(request)
    return render(request, 'login.html', {"success": "You have been logged out successfully!"})

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




