from django.shortcuts import render,redirect,HttpResponse
from groq import Groq
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import WishlistItem  # Import the model
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.models import User # this is for sign Up
from django.contrib.auth import authenticate, login, logout
#from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
#email validator
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import tensorflow as tf
import numpy as np
import os
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
import os
from django.conf import settings
from keras.preprocessing import image
import cv2

model_path = os.path.join(settings.BASE_DIR, 'models', 'trained_model (1).h5')
cnn = tf.keras.models.load_model(model_path)

CLASS_NAMES = [
    'apple', 'banana', 'beetroot', 'bell pepper', 'cabbage', 'capsicum', 'carrot',
    'cauliflower', 'chilli pepper', 'corn', 'cucumber', 'eggplant', 'garlic',
    'ginger', 'grapes', 'jalepeno', 'kiwi', 'lemon', 'lettuce', 'mango', 'onion',
    'orange', 'paprika', 'pear', 'peas', 'pineapple', 'pomegranate', 'potato',
    'raddish', 'soy beans', 'spinach', 'sweetcorn', 'sweetpotato', 'tomato',
    'turnip', 'watermelon'
]
# Home view
def home(request):
    return render(request, "home2.html")

# Generate recipe view
def generate(request):
    return render(request, "generate.html")
def profile(request):
    return render(request, "profile.html")



def signup(request):
    if request.method == 'POST':
        uname = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
         # Validate email format
        try:
            validate_email(email)  # Raises ValidationError if invalid
        except ValidationError:
          
            return render(request, 'signup.html', {'error':'Email format is not correct'})
        
        if password1!=password2:
             return render(request, 'signup.html', {'error': 'Password1 and password2 are not same!!'})
           # return HttpResponse("Your password and confirm password are not same")
        else:
         my_user = User.objects.create_user(uname, email,password1)
         my_user.save()
         return redirect('index-page')
      
        
    return render(request, 'signup.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        pass1 = request.POST.get('password')
        user=authenticate(request,username=username, password = pass1)
        if user is not None:
            login(request,user)
            return redirect('index-page')
        else:
             return render(request, 'login.html', {'error': 'Username or Password is incorrect!!'})
          #  return HttpResponse("Username or Password is incorrect!!")
    return render(request, 'login.html')


@login_required(login_url='login')
def LogoutPage(request):
    logout(request)
    return render(request, 'login.html', {"success": "You have been logged out successfully!"})

# Wishlist view
def wishlist(request):
    items = WishlistItem.objects.all()  # Fetch all wishlist items from the database
    return render(request, "wishlist.html", {'students': items})  # Pass items to the template

def recip(itemss, diet_type="", regional=""):
    try:
        client = Groq(api_key=os.getenv('GROQ_API_KEY'))

        # Build the prompt with additional preferences
        system_prompt = "You are a recipe generator that creates delicious recipes based on given ingredients and preferences."
        
        user_prompt = f"Generate a recipe using the following ingredients: {itemss}"
        
        # Add diet type preference if provided
        if diet_type:
            user_prompt += f"\nDiet preference: {diet_type}"
        
        # Add regional preference if provided
        if regional:
            user_prompt += f"\nRegional cuisine preference: {regional}"
        
        # Add additional instructions for better recipe generation
        user_prompt += "\n\nPlease provide a detailed recipe including:\n- Preparation time\n- Cooking time\n- Servings\n- Step-by-step instructions\n- Any additional tips or variations"

        prompt = client.chat.completions.create(
           model="llama-3.1-8b-instant",
           messages=[
               {
                   "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
       )
        
        recipe = prompt.choices[0].message.content
        return recipe
    except Exception as e:
        print(f"Groq API error: {e}")
        return f"Error generating recipe: {str(e)}"

# @csrf_exempt
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
    




def upload_image(request):
    if request.method == 'POST' and request.FILES.get('image'):
        try:
            # Get the uploaded image
            uploaded_image = request.FILES['image']

            # Validate file extension
            valid_extensions = ['.jpg', '.jpeg', '.png']
            ext = os.path.splitext(uploaded_image.name)[1].lower()
            if ext not in valid_extensions:
                return render(request, 'classify/upload.html', {
                    'error': 'Please upload a JPG, JPEG, or PNG image.'
                })

            # Save the image temporarily
            temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
            os.makedirs(temp_dir, exist_ok=True)
            temp_image_path = os.path.join(temp_dir, uploaded_image.name)

            with open(temp_image_path, 'wb+') as destination:
                for chunk in uploaded_image.chunks():
                    destination.write(chunk)

            # Process the image using the same method as your working Colab code
            # Reading an image in default mode
            img = cv2.imread(temp_image_path)
            if img is None:
                return render(request, 'classify/upload.html', {
                    'error': 'Could not read the uploaded image.'
                })

            # Convert BGR to RGB (same as your Colab code)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            # Use tf.keras.preprocessing.image.load_img like in your Colab code
            image = tf.keras.preprocessing.image.load_img(temp_image_path, target_size=(64, 64))
            input_arr = tf.keras.preprocessing.image.img_to_array(image)
            input_arr = np.array([input_arr])  # Convert single image to a batch

            # Make prediction using the same method as your Colab code
            predictions = cnn.predict(input_arr)
            result_index = np.argmax(predictions)  # Return index of max element
            predicted_class = CLASS_NAMES[result_index]
            confidence = float(predictions[0][result_index]) * 100

            # Debug: Print predictions like in your Colab code
            print(f"Result index: {result_index}")
            print(f"It's a {predicted_class}")
            print(f"All predictions: {predictions[0]}")

            # Get top 5 predictions for debugging
            top_5_indices = np.argsort(predictions[0])[-5:][::-1]
            print("Top 5 predictions:")
            for i, idx in enumerate(top_5_indices):
                print(f"{i+1}. {CLASS_NAMES[idx]}: {predictions[0][idx]*100:.2f}%")

            # Check for model bias
            cabbage_index = CLASS_NAMES.index('cabbage')
            cabbage_rank = np.where(top_5_indices == cabbage_index)[0]
            has_bias = len(cabbage_rank) > 0 and cabbage_rank[0] <= 2
            if has_bias:
                print("WARNING: Model shows bias towards cabbage")

            # Prepare context for template
            context = {
                'uploaded_image_url': f"{settings.MEDIA_URL}temp/{uploaded_image.name}",
                'predicted_class': predicted_class,
                'confidence': round(confidence, 2),
                'class_names': CLASS_NAMES,
                'debug_info': {
                    'image_shape': input_arr.shape,
                    'all_predictions': predictions[0].tolist(),
                    'top_5_predictions': [(CLASS_NAMES[idx], float(predictions[0][idx]*100)) for idx in top_5_indices],
                    'model_bias_warning': has_bias,
                    'result_index': result_index
                }
            }

            return render(request, 'classify/result.html', context)

        except Exception as e:
            # Log the error for debugging
            print(f"Error processing image: {str(e)}")
            import traceback
            traceback.print_exc()
            return render(request, 'classify/upload.html', {
                'error': f'An error occurred while processing your image: {str(e)}'
            })

    return render(request, 'classify/upload.html')

@csrf_exempt
def ai_scan_predict(request):
    if request.method == 'POST':
        try:
            import base64
            from PIL import Image
            import io

            # Get base64 image data
            image_data = request.POST.get('image')
            if not image_data:
                return JsonResponse({'error': 'No image data provided'}, status=400)

            # Decode base64
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]
            image_bytes = base64.b64decode(imgstr)

            # Convert to PIL Image
            image = Image.open(io.BytesIO(image_bytes))

            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')

            # Resize to 64x64
            image = image.resize((64, 64))

            # Convert to array
            input_arr = tf.keras.preprocessing.image.img_to_array(image)
            input_arr = np.array([input_arr])  # Convert single image to a batch

            # Make prediction
            predictions = cnn.predict(input_arr)
            result_index = np.argmax(predictions)
            predicted_class = CLASS_NAMES[result_index]
            confidence = float(predictions[0][result_index]) * 100

            return JsonResponse({
                'predicted_class': predicted_class,
                'confidence': round(confidence, 2)
            })

        except Exception as e:
            print(f"Error in ai_scan_predict: {str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)
