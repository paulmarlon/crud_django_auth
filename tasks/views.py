# Permite renderizar plantillas HTML y redirigir a otras URLs o vistas del proyecto
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

# Formularios y autenticación de Django
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from .forms import TaskForm
from .models import Task


# Vista para la página de inicio
def home(request):
    return render(request, "home.html")


# Vista para el registro de nuevos usuarios
def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("tasks")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
            return render(request, "signup.html", {"form": form})
    else:
        form = UserCreationForm()

    return render(request, "signup.html", {"form": form})


# Vista para listar tareas pendientes
@login_required
def tasks(request):
    # Obtenemos todas las tareas pendientes del usuario
    task_list = Task.objects.filter(
        user=request.user, datecompleted__isnull=True
    ).order_by("-created")

    # Configuramos el paginador: 15 tareas por página
    paginator = Paginator(task_list, 15)
    page_number = request.GET.get("page")
    tasks = paginator.get_page(page_number)

    return render(request, "tasks.html", {"tasks": tasks})


@login_required
def tasks_completed(request):
    tasks = Task.objects.filter(
        user=request.user, datecompleted__isnull=False
    ).order_by("-datecompleted")
    return render(request, "tasks.html", {"tasks": tasks})


# Vista para el cierre de sesión
def signout(request):
    logout(request)
    return redirect("home")


# Vista para el inicio de sesión de usuarios registrados
def signin(request):
    if request.method == "GET":
        return render(request, "signin.html", {"form": AuthenticationForm()})
    else:
        user = authenticate(
            request,
            username=request.POST.get("username"),
            password=request.POST.get("password"),
        )

        if user is None:
            messages.error(request, "Usuario o contraseña incorrectos.")
            return render(
                request,
                "signin.html",
                {"form": AuthenticationForm(request.POST)},
            )

        login(request, user)
        messages.success(request, "¡Bienvenido de nuevo!")
        return redirect("tasks")


# Vista para crear una tarea nueva
@login_required
def create_task(request):
    if request.method == "GET":
        return render(request, "create_task.html", {"form": TaskForm()})
    else:
        form = TaskForm(request.POST)
        if form.is_valid():
            new_task = form.save(commit=False)
            new_task.user = request.user
            new_task.save()
            messages.success(request, "¡Tarea creada exitosamente!")
            return redirect("tasks")
        else:
            messages.error(request, "Por favor, corrige los errores en el formulario.")
            return render(request, "create_task.html", {"form": form})


# Vista para ver y actualizar los detalles de una tarea
@login_required
def task_detail(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect("tasks")
    else:
        form = TaskForm(instance=task)

    return render(request, "task_detail.html", {"task": task, "form": form})


# Vista para marcar una tarea como completada
@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == "POST":
        task.datecompleted = timezone.now()
        task.save()
        return redirect("tasks")


# Vista para eliminar una tarea
@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == "POST":
        task.delete()
        messages.success(request, "¡Tarea eliminada exitosamente!")
        return redirect("tasks")
