# capa de vista/presentación

from django.shortcuts import redirect, render
from .layers.services import services
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.contrib.auth import login
from .forms import CustomUserRegisterForm

def index_page(request):
    return render(request, 'index.html')

# esta función obtiene 2 listados: uno de las imágenes de la API y otro de favoritos, ambos en formato Card, y los dibuja en el template 'home.html'.
def home(request):
    images = services.getAllImages()
    favourite_list = []
    if request.user.is_authenticated:
        favourite_list = services.getAllFavouritesByUser(request.user)
    return render(request, 'home.html', {'images': images, 'favourite_list': favourite_list})
# función utilizada en el buscador.
def search(request):
    name = request.POST.get('query', '').lower()

    # si el usuario ingresó algo en el buscador, se deben filtrar las imágenes por dicho ingreso.
    if name:
        images = [img for img in services.getAllImages() if name in img.name.lower()]
        favourite_list = services.getAllFavouritesByUser(request.user) if request.user.is_authenticated else []

        return render(request, 'home.html', { 'images': images, 'favourite_list': favourite_list })
    else:
        return redirect('home')

# función utilizada para filtrar por el tipo del Pokemon
def filter_by_type(request):
    type_filter = request.POST.get('type', '').lower()

    if type_filter:
        images = [img for img in services.getAllImages() if type_filter in img.types]
        favourite_list = services.getAllFavouritesByUser(request.user) if request.user.is_authenticated else []

        return render(request, 'home.html', {'images': images, 'favourite_list': favourite_list})
    else:
        return redirect('home')

# Estas funciones se usan cuando el usuario está logueado en la aplicación.
@login_required
def getAllFavouritesByUser(request):
    from .models import Favourite
    from .layers.utilities.translator import fromRepositoryIntoCard

    raw_favourites = Favourite.objects.filter(user=request.user)
    favourite_cards = [
        fromRepositoryIntoCard({
            'id': fav.id,
            'name': fav.name,
            'height': fav.height,
            'weight': fav.weight,
            'base_experience': 0,
            'types': fav.types,
            'image': fav.image
        })
        for fav in raw_favourites
    ]

    return render(request, 'favourites.html', {
        'favourite_list': favourite_cards
    })

@login_required
def saveFavourite(request):
    from .models import Favourite
    name = request.POST.get("name")
    image = request.POST.get("image")
    types = request.POST.get("types")
    height = request.POST.get("height")
    weight = request.POST.get("weight")

    # Verificamos si ya fue añadido
    exists = Favourite.objects.filter(user=request.user, name=name).exists()
    if not exists:
        fav = Favourite(user=request.user, name=name, image=image, types=types, height=height, weight=weight)
        fav.save()

    return redirect('home')

@login_required
def deleteFavourite(request):
    from .models import Favourite
    name = request.POST.get("name")

    Favourite.objects.filter(user=request.user, name=name).delete()

    return redirect('home')   # o 'home' si preferís volver a la galería


@login_required
def exit(request):
    logout(request)
    return redirect('home')


def registro(request):
    if request.method == 'POST':
        form = CustomUserRegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            if User.objects.filter(username=username).exists():
                messages.error(request, "⚠️ Ese nombre de usuario ya está en uso.")
            else:
                user = User.objects.create_user(
                    username=username,
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password'],
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name']
                )

                # ✉️ OPCIONAL: envío de correo de bienvenida
                try:
                    send_mail(
                        '🎉 Registro exitoso en Pokédex',
                        f"Hola {user.first_name}, ¡gracias por registrarte! Tu usuario es: {user.username}",
                        'tucorreo@gmail.com',
                        [user.email],
                        fail_silently=False,
                    )
                except Exception as e:
                     print("⚠️ Error al enviar correo:", e)

                login(request, user)
                messages.success(request, f"🟢 ¡Bienvenido {user.first_name}! Ya sos parte de la Pokédex.")
                return redirect('home')
    else:
        form = CustomUserRegisterForm()

    return render(request, 'registro.html', {'form': form})