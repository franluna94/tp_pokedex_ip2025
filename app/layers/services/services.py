# capa de servicio/lógica de negocio

from ..transport import transport
from ...config import config
from ..persistence import repositories
from ..utilities import translator
from django.contrib.auth import get_user
from app.models import Favourite

# función que devuelve un listado de cards. Cada card representa una imagen de la API de Pokemon
def getAllImages():
    # debe ejecutar los siguientes pasos:
    # 1) traer un listado de imágenes crudas desde la API (ver transport.py)
    raw_images = transport.getAllImages()
    # 2) convertir cada img. en una card.
    cards = [translator.fromRequestIntoCard(img) for img in raw_images]
    # 3) añadirlas a un nuevo listado que, finalmente, se retornará con todas las card encontradas.
    return cards

# función que filtra según el nombre del pokemon.
def filterByCharacter(name):
    filtered_cards = []

    for card in getAllImages():
        # debe verificar si el name está contenido en el nombre de la card, antes de agregarlo al listado de filtered_cards.
        filtered_cards.append(card)

    return filtered_cards

# función que filtra las cards según su tipo.
def filterByType(type_filter):
    filtered_cards = []

    for card in getAllImages():
        if type_filter in card.types:
            filtered_cards.append(card)

    return filtered_cards


# añadir favoritos (usado desde el template 'home.html')
from django.contrib.auth import get_user
from app.layers.utilities.translator import fromTemplateIntoCard
from app.layers.persistence import repositories


def saveFavourite(request):
    user = get_user(request)

    # Paso 1: transformar el request en una Card
    fav = fromTemplateIntoCard(request)

    # Paso 2: asignarle el usuario autenticado
    fav.user = user

    # Paso 3: guardar el favorito en la base
    return repositories.save_favourite(fav)# lo guardamos en la BD.

# usados desde el template 'favourites.html'
from django.contrib.auth import get_user
from app.models import Favourite
from app.layers.utilities.translator import fromRepositoryIntoCard

def getAllFavourites(request):
    if not request.user.is_authenticated:
        return []

    user = get_user(request)
    favourite_list = Favourite.objects.filter(user=user)

    mapped_favourites = [
        fromRepositoryIntoCard({
            'id': fav.id,
            'name': fav.name,
            'height': fav.height,
            'weight': fav.weight,
            'base_experience': 0,
            'types': fav.types,
            'image': fav.image
        })
        for fav in favourite_list
    ]

    return mapped_favourites
    
def getAllFavouritesByUser(user):
    return Favourite.objects.filter(user=user)


def deleteFavourite(request):
    favId = request.POST.get('id')
    return repositories.delete_favourite(favId) # borramos un favorito por su ID

#obtenemos de TYPE_ID_MAP el id correspondiente a un tipo segun su nombre
def get_type_icon_url_by_name(type_name):
    type_id = config.TYPE_ID_MAP.get(type_name.lower())
    if not type_id:
        return None
    return transport.get_type_icon_url_by_id(type_id)

