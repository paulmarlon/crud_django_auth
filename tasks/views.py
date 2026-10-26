# Permite renderizar plantillas HTML y redirigir a otras URLs o vistas del proyecto
from django.shortcuts import render, redirect

# Formulario nativo de Django que maneja de forma segura el registro de usuarios
# (incluyendo la creación del hash de contraseña y la validación de que coincidan)
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from django.contrib import messages

# Función nativa de Django para iniciar sesión a un usuario programáticamente
# (útil si quieres loguearlo automáticamente justo después de registrarse)
from django.contrib.auth import login, logout, authenticate


# Vista para la página de inicio
def home(request):
    return render(request, "home.html")


# Vista para el registro de nuevos usuarios
def signup(request):
    # Si el método es POST, significa que el usuario envió el formulario con sus datos
    if request.method == "POST":
        # 1. Instanciamos el formulario de creación de usuarios de Django con los datos recibidos
        form = UserCreationForm(request.POST)

        # 2. form.is_valid() valida automáticamente:
        #    - Que los campos obligatorios estén llenos.
        #    - Que las dos contraseñas coincidan exactamente.
        #    - Que la contraseña cumpla con los requisitos mínimos de seguridad.
        #    - Que el nombre de usuario no esté duplicado en la base de datos.
        if form.is_valid():
            # Guardamos el usuario de forma segura (hashea la contraseña automáticamente)
            user = form.save()

            # (Opcional) Podemos iniciar sesión automáticamente tras registrarse
            login(request, user)

            # Redirigimos a la página de inicio o login tras un registro exitoso
            return redirect("tasks")
        else:
            # Recorremos los errores específicos que detectó el formulario
            for field, errors in form.errors.items():
                for error in errors:
                    # Enviamos cada error específico a la cabecera
                    messages.error(request, error)
            return render(request, "signup.html", {"form": form})

    # Si el método es GET, simplemente mostramos el formulario de registro vacío
    else:
        form = UserCreationForm()

    return render(request, "signup.html", {"form": form})


def tasks(request):
    return render(request, "tasks.html")


# Vista para el cierrre de sesion
def signout(request):
    logout(request)
    return redirect("home")


# Vista para el acceso a sesion usuarios ya registrados
def signin(request):
    if request.method == "GET":
        # Pasamos una instancia vacía del formulario AuthenticationForm()
        return render(request, "signin.html", {"form": AuthenticationForm()})
    else:
        # Autenticamos al usuario con los datos del POST
        user = authenticate(
            request,
            username=request.POST.get("username"),
            password=request.POST.get("password"),
        )

        if user is None:
            # Si los datos son incorrectos, enviamos un mensaje a la cabecera
            messages.error(request, "Usuario o contraseña incorrectos.")
            return render(
                request,
                "signin.html",
                {"form": AuthenticationForm(request.POST)},
            )

        # Si todo es correcto, iniciamos sesión y redirigimos a home
        login(request, user)
        messages.success(request, "¡Bienvenido de nuevo!")
        return redirect("tasks")
