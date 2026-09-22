# import base64
#
# from django.shortcuts import render
#
# # ако web_pipeline.py ти е во django/ директно:
# from web_pipeline import (
#     solve_from_text,
#     solve_from_image_bytes,
#     solve_from_pdf_bytes,
# )
#
# # ако е во app, на пример solver/web_pipeline.py:
# # from solver.web_pipeline import (
# #     solve_from_text,
# #     solve_from_image_bytes,
# #     solve_from_pdf_bytes,
# # )
#
#
# def home(request):
#     result = None
#
#     if request.method == "POST":
#         text_input = (request.POST.get("text_input") or "").strip()
#
#         uploaded_file = request.FILES.get("file_input")
#         camera_image_data = request.POST.get("camera_image")          # data URL или ""
#         pasted_file_data = request.POST.get("pasted_file_data")       # data URL или ""
#         pasted_file_type = request.POST.get("pasted_file_type")       # image/... или application/pdf
#
#         try:
#             # 1) Ако има upload-нат фајл (слика или PDF)
#             if uploaded_file:
#                 content = uploaded_file.read()
#                 content_type = uploaded_file.content_type or ""
#
#                 if content_type.startswith("image/"):
#                     result = solve_from_image_bytes(content)
#                 elif content_type == "application/pdf":
#                     result = solve_from_pdf_bytes(content)
#                 else:
#                     result = f"Неподдржан тип на фајл: {content_type}"
#
#             # 2) Ако има слика од камерата (base64 data URL)
#             elif camera_image_data:
#                 header, encoded = camera_image_data.split(",", 1)
#                 image_bytes = base64.b64decode(encoded)
#                 result = solve_from_image_bytes(image_bytes)
#
#             # 3) Ако има pasted фајл (слика или PDF)
#             elif pasted_file_data and pasted_file_type:
#                 header, encoded = pasted_file_data.split(",", 1)
#                 file_bytes = base64.b64decode(encoded)
#
#                 if pasted_file_type.startswith("image/"):
#                     result = solve_from_image_bytes(file_bytes)
#                 elif pasted_file_type == "application/pdf":
#                     result = solve_from_pdf_bytes(file_bytes)
#                 else:
#                     result = f"Неподдржан pasted тип: {pasted_file_type}"
#
#             # 4) Ако има само текст
#             elif text_input:
#                 result = solve_from_text(text_input)
#
#             else:
#                 result = "Немаш внесено текст, слика или PDF."
#         except Exception as e:
#             result = f"Настана грешка во pipeline: {e}"
#
#     return render(request, "home.html", {"result": result})
import base64

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST


from web_pipeline import solve_from_image_bytes, solve_from_pdf_bytes, solve_from_text


# import base64
#
# from django.shortcuts import render
#
# # ако web_pipeline.py ти е во django/ директно:
# from web_pipeline import (
#     solve_from_text,
#     solve_from_image_bytes,
#     solve_from_pdf_bytes,
# )
#
# # ако е во app, на пример solver/web_pipeline.py:
# # from solver.web_pipeline import (
# #     solve_from_text,
# #     solve_from_image_bytes,
# #     solve_from_pdf_bytes,
# # )
#
#
# def home(request):
#     result = None
#
#     if request.method == "POST":
#         text_input = (request.POST.get("text_input") or "").strip()
#
#         uploaded_file = request.FILES.get("file_input")
#         camera_image_data = request.POST.get("camera_image")          # data URL или ""
#         pasted_file_data = request.POST.get("pasted_file_data")       # data URL или ""
#         pasted_file_type = request.POST.get("pasted_file_type")       # image/... или application/pdf
#
#         try:
#             # 1) Ако има upload-нат фајл (слика или PDF)
#             if uploaded_file:
#                 content = uploaded_file.read()
#                 content_type = uploaded_file.content_type or ""
#
#                 if content_type.startswith("image/"):
#                     result = solve_from_image_bytes(content)
#                 elif content_type == "application/pdf":
#                     result = solve_from_pdf_bytes(content)
#                 else:
#                     result = f"Неподдржан тип на фајл: {content_type}"
#
#             # 2) Ако има слика од камерата (base64 data URL)
#             elif camera_image_data:
#                 header, encoded = camera_image_data.split(",", 1)
#                 image_bytes = base64.b64decode(encoded)
#                 result = solve_from_image_bytes(image_bytes)
#
#             # 3) Ако има pasted фајл (слика или PDF)
#             elif pasted_file_data and pasted_file_type:
#                 header, encoded = pasted_file_data.split(",", 1)
#                 file_bytes = base64.b64decode(encoded)
#
#                 if pasted_file_type.startswith("image/"):
#                     result = solve_from_image_bytes(file_bytes)
#                 elif pasted_file_type == "application/pdf":
#                     result = solve_from_pdf_bytes(file_bytes)
#                 else:
#                     result = f"Неподдржан pasted тип: {pasted_file_type}"
#
#             # 4) Ако има само текст
#             elif text_input:
#                 result = solve_from_text(text_input)
#
#             else:
#                 result = "Немаш внесено текст, слика или PDF."
#         except Exception as e:
#             result = f"Настана грешка во pipeline: {e}"
#
#     return render(request, "home.html", {"result": result})
import base64

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from agent.normalization import clean_prompt
from web_pipeline import solve_from_image_bytes, solve_from_pdf_bytes, solve_from_text


def home(request):
    result = None
    if request.method == "POST":
        text_input = (request.POST.get("text_input") or "")
        uploaded_file = request.FILES.get("file_input")
        camera_image_data = request.POST.get("camera_image")          # data URL или ""
        pasted_file_data = request.POST.get("pasted_file_data")       # data URL или ""
        pasted_file_type = request.POST.get("pasted_file_type")       # image/... или application/pdf

        try:
            # 1) Ако има upload-нат фајл (слика или PDF)
            if uploaded_file:
                content = uploaded_file.read()
                content_type = uploaded_file.content_type or ""

                if content_type.startswith("image/"):
                    result = solve_from_image_bytes(content)
                elif content_type == "application/pdf":
                    result = solve_from_pdf_bytes(content)
                else:
                    result = f"Неподдржан тип на фајл: {content_type}"

            # 2) Ако има слика од камерата (base64 data URL)
            elif camera_image_data:
                header, encoded = camera_image_data.split(",", 1)
                image_bytes = base64.b64decode(encoded)
                result = solve_from_image_bytes(image_bytes)

            # 3) Ако има pasted фајл (слика или PDF)
            elif pasted_file_data and pasted_file_type:
                header, encoded = pasted_file_data.split(",", 1)
                file_bytes = base64.b64decode(encoded)

                if pasted_file_type.startswith("image/"):
                    result = solve_from_image_bytes(file_bytes)
                elif pasted_file_type == "application/pdf":
                    result = solve_from_pdf_bytes(file_bytes)
                else:
                    result = f"Неподдржан pasted тип: {pasted_file_type}"

            # 4) Ако има само текст
            elif text_input:
                result = solve_from_text(text_input)

            else:
                result = "Немаш внесено текст, слика или PDF."
        except Exception as e:
            result = f"Настана грешка во pipeline: {e}"


    return render(request, "home.html", {"result": result, "history": []})



def signup_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        if not username or not password:
            return render(request, "auth/signup.html", {"error": "Username и password се задолжителни.", "history": []})

        if User.objects.filter(username=username).exists():
            return render(request, "auth/signup.html", {"error": "Username веќе постои.", "history": []})

        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        login(request, user)
        return redirect("home")

    return render(request, "auth/signup.html", {"history": []})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(request, username=username, password=password)
        if user is None:
            return render(request, "auth/login.html", {"error": "Погрешен username или password.", "history": []})

        login(request, user)
        return redirect("home")

    return render(request, "auth/login.html", {"history": []})


@require_POST
def logout_view(request):
    logout(request)
    return redirect("home")


@login_required
def profile_view(request):
    if request.method == "POST":
        request.user.first_name = request.POST.get("first_name", "").strip()
        request.user.last_name = request.POST.get("last_name", "").strip()

        new_username = request.POST.get("username", "").strip()
        if new_username and new_username != request.user.username:
            if User.objects.filter(username=new_username).exclude(id=request.user.id).exists():
                return render(request, "auth/profile.html", {"error": "Username веќе постои.", "history": []})
            request.user.username = new_username

        new_pw = request.POST.get("password", "").strip()
        if new_pw:
            request.user.set_password(new_pw)

        request.user.save()

        # ако смениш password, мора повторно login
        if new_pw:
            login(request, request.user)

        return redirect("home")

    return render(request, "auth/profile.html", {"history": []})

def signup_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        if not username or not password:
            return render(request, "auth/signup.html", {"error": "Username и password се задолжителни.", "history": []})

        if User.objects.filter(username=username).exists():
            return render(request, "auth/signup.html", {"error": "Username веќе постои.", "history": []})

        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        login(request, user)
        return redirect("home")

    return render(request, "auth/signup.html", {"history": []})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(request, username=username, password=password)
        if user is None:
            return render(request, "auth/login.html", {"error": "Погрешен username или password.", "history": []})

        login(request, user)
        return redirect("home")

    return render(request, "auth/login.html", {"history": []})


@require_POST
def logout_view(request):
    logout(request)
    return redirect("home")


@login_required
def profile_view(request):
    if request.method == "POST":
        request.user.first_name = request.POST.get("first_name", "").strip()
        request.user.last_name = request.POST.get("last_name", "").strip()

        new_username = request.POST.get("username", "").strip()
        if new_username and new_username != request.user.username:
            if User.objects.filter(username=new_username).exclude(id=request.user.id).exists():
                return render(request, "auth/profile.html", {"error": "Username веќе постои.", "history": []})
            request.user.username = new_username

        new_pw = request.POST.get("password", "").strip()
        if new_pw:
            request.user.set_password(new_pw)

        request.user.save()

        # ако смениш password, мора повторно login
        if new_pw:
            login(request, request.user)

        return redirect("home")

    return render(request, "auth/profile.html", {"history": []})