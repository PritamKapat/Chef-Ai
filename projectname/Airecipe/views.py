from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from groq import Groq
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import WishlistItem, InventoryItem
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import os
from django.conf import settings
from datetime import date
import requests
# YOLO IMPORTS
from ultralytics import YOLO
from PIL import Image
import base64
import io
# -------- HELPER: Build prompt for the AI image model --------
def build_image_prompt(recipe_text):
    return f"""
    Generate a photorealistic food image of the cooked recipe described below.

    RECIPE DESCRIPTION:
    {recipe_text}

    IMPORTANT:
    - Show only the final cooked dish.
    - Do NOT generate any live chicken, bird, or animals.
    - Present the dish in a plate or bowl, restaurant style.
    - Vivid, realistic, well-lit food photography.
    """

# -------- EURI (FLUX.1 Schnell) API CONFIG --------
EURI_URL = "https://api.euron.one/api/v1/euri/images/generations"

EURI_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "Bearer euri-2807cdf05a0833cd282be8c8beccbbaad85ee1770cc580fe721bb33574407f20"
}


# -------- MAIN DJANGO VIEW --------
@csrf_exempt
def generate_recipe_image(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    try:
        data = json.loads(request.body)
        recipe_text = data.get("recipe")

        if not recipe_text:
            return JsonResponse({"error": "Recipe text missing"}, status=400)

        # Build prompt for the image generator
        payload = {
            "prompt": build_image_prompt(recipe_text),
            "model": "black-forest-labs/FLUX.1-schnell",
            "n": 1,
            "size": "1024x1024",
            "response_format": "url"
        }

        # API call
        response = requests.post(EURI_URL, headers=EURI_HEADERS, json=payload)

        if response.status_code == 200:
            img_data = response.json()
            img_url = img_data["data"][0]["url"]    # URL of generated image

            return JsonResponse({"image_url": img_url})

        else:
            return JsonResponse({
                "error": "EuriAI request failed",
                "details": response.text
            }, status=500)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
# -------------------------------
# LOAD YOLO MODEL (GLOBAL)
# -------------------------------
yolo_model_path = os.path.join(settings.BASE_DIR, "models", "best2.pt")
yolo = YOLO(yolo_model_path)


# -------------------------------
# BASIC PAGES
# -------------------------------
def home(request):
    return render(request, "home2.html")


def inventory_page(request):
    items = InventoryItem.objects.all()

    expiring = []
    for i in items:
        if i.expiry_status in ["danger", "warning"]:
            expiring.append({
                "name": i.name,
                "expiry_status": i.expiry_status,
                "expiry_text": i.expiry_text
            })

    context = {
        "inventory_items": items,
        "expiring_items": expiring
    }
    return render(request, "inventory.html", context)


def generate(request):
    inventory_items = InventoryItem.objects.all()
    return render(request, "generate.html", {"inventory_items": inventory_items})


def profile(request):
    return render(request, "profile.html")


# -------------------------------
# INVENTORY CRUD
# -------------------------------
def add_inventory(request):
    if request.method == "POST":
        name = request.POST.get("name")
        quantity = request.POST.get("quantity")
        unit = request.POST.get("unit")
        storage = request.POST.get("storage")
        expiry = request.POST.get("expiry_date")

        InventoryItem.objects.create(
            name=name,
            quantity=quantity,
            unit=unit,
            storage=storage,
            expiry_date=expiry
        )

    return redirect("inventory")


def edit_inventory(request):
    if request.method == "POST":
        item_id = request.POST.get("id")
        item = get_object_or_404(InventoryItem, id=item_id)

        item.name = request.POST.get("name")
        item.quantity = request.POST.get("quantity")
        item.unit = request.POST.get("unit")
        item.storage = request.POST.get("storage")
        item.expiry_date = request.POST.get("expiry_date")
        item.save()

    return redirect("inventory")


def delete_inventory(request):
    if request.method == "POST":
        item_id = request.POST.get("id")
        item = get_object_or_404(InventoryItem, id=item_id)
        item.delete()
    return redirect("inventory")


@csrf_exempt
def deduct_inventory(request):
    if request.method == "POST":
        data = json.loads(request.body)
        items = data.get("items")  # format: "tomato:2pcs, onion:1pcs"

        try:
            for pair in items.split(","):
                pair = pair.strip()
                if not pair:
                    continue

                name, qty_unit = pair.split(":")
                qty = ''.join(filter(str.isdigit, qty_unit))

                item = InventoryItem.objects.filter(name__iexact=name).first()
                if item:
                    item.quantity -= int(qty)
                    if item.quantity <= 0:
                        item.delete()
                    else:
                        item.save()

            return JsonResponse({"success": True})

        except Exception as e:
            return JsonResponse({"error": str(e)})

    return JsonResponse({"error": "Invalid request"}, status=400)


# -------------------------------
# USER AUTH
# -------------------------------
def signup(request):
    if request.method == 'POST':
        uname = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        try:
            validate_email(email)
        except ValidationError:
            return render(request, 'signup.html', {'error': 'Invalid email format'})

        if password1 != password2:
            return render(request, 'signup.html', {'error': 'Passwords do not match!'})

        User.objects.create_user(uname, email, password1)
        return redirect('index-page')

    return render(request, 'signup.html')


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        pass1 = request.POST.get('password')
        user = authenticate(request, username=username, password=pass1)
        if user:
            login(request, user)
            return redirect('index-page')
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password!'})

    return render(request, 'login.html')


@login_required(login_url='login')
def LogoutPage(request):
    logout(request)
    return render(request, 'login.html', {"success": "Logged out successfully!"})


# -------------------------------
# WISHLIST
# -------------------------------
def wishlist(request):
    items = WishlistItem.objects.all()
    return render(request, "wishlist.html", {'students': items})


def delete_item(request, id):
    item = get_object_or_404(WishlistItem, id=id)
    item.delete()
    return redirect('wishlist-page')


def update(request, id):
    student = WishlistItem.objects.get(id=id)
    if request.method == "POST":
        description = request.POST.get('pdescription')
        if description:
            student.description = description
            student.save()
            return redirect('wishlist-page')
    return render(request, "update.html", {'student': student})


@csrf_exempt
def add_to_wishlist(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            items = data.get('items')
            recipe = data.get('recipe')

            if not items or not recipe:
                return JsonResponse({'error': 'Missing items or recipe'}, status=400)

            WishlistItem.objects.create(items=items, description=recipe)
            return JsonResponse({'success': True})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)


# -------------------------------
# RECIPE GENERATION (GROQ)
# -------------------------------
def recip(itemss, diet_type="", regional=""):
    try:
        client = Groq(api_key=os.getenv('GROQ_API_KEY'))

        system_prompt = "You are a recipe generator."
        user_prompt = f"Generate a recipe using: {itemss}"

        if diet_type:
            user_prompt += f"\nDiet preference: {diet_type}"
        if regional:
            user_prompt += f"\nRegional cuisine: {regional}"

        user_prompt += "\nPlease include prep time, cook time, servings, and steps."

        prompt = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
        )

        return prompt.choices[0].message.content

    except Exception as e:
        return f"Error generating recipe: {str(e)}"


@csrf_exempt
def generate_recipe(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        items = data.get('items')

        recipe = recip(items)

        return JsonResponse({'recipe': recipe})

    return JsonResponse({'error': 'Invalid request'}, status=400)


# -------------------------------
# YOLO IMAGE INGREDIENT DETECTION
# -------------------------------
@csrf_exempt
def ai_scan_predict(request):
    """
    This view receives a base64 image from frontend,
    runs YOLOv8 detection, and returns detected ingredient names + confidence.
    """
    if request.method == 'POST':
        try:
            # Read Base64 image
            image_data = request.POST.get('image')
            if not image_data:
                return JsonResponse({'error': 'No image data provided'}, status=400)

            # Decode base64
            format, imgstr = image_data.split(';base64,')
            img_bytes = base64.b64decode(imgstr)

            # Convert to PIL image
            image = Image.open(io.BytesIO(img_bytes)).convert("RGB")

            # YOLO prediction
            results = yolo.predict(image, imgsz=640)
            detections = []

            r = results[0]
            for box in r.boxes:
                cls_id = int(box.cls[0])
                name = r.names[cls_id]
                conf = float(box.conf[0])

                detections.append({
                    "name": name,
                    "confidence": round(conf, 3)
                })

            return JsonResponse({
                "ingredients": detections,
                "count": len(detections)
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)
