# wsgi.py
# pylint: disable=missing-docstring
# pylint: disable=missing-docstring
# pylint: disable=too-few-public-methods

import itertools

from flask import Flask, jsonify, abort, request
app = Flask(__name__)


# Préfixer le chemin de l'api en utilisant un numéro de version est vraiment important pour gérer les futures évolutions.
# De cette façon, nous pouvons continuer à proposer l'ancien service en utilisant l'url /v1 et proposer le nouveau service en utilisant /v2.
# Nous supprimerons l'api /v1 (et le code associé) lorsque tous nos utilisateurs utiliseront l'url /v2.
BASE_URL = '/api/v1'

# N'oubliez pas qu'il ne s'agit que d'une simulation de base de données très simple.
# Ces données ne sont conservées que dans la RAM : si vous redémarrez votre serveur, les modifications sont perdues.
# Ne vous inquiétez pas pour cela, notre but aujourd'hui est de comprendre l'API REST, pas de vraiment stocker des données.
PRODUCTS = {
    1: { 'id': 1, 'name': 'Skello' },
    2: { 'id': 2, 'name': 'Socialive.tv' },
    3: { 'id': 3, 'name': 'Le Wagon'},
}

# C'est une façon simple et naïve de générer des id consécutifs (comme le ferait une base de données).
START_INDEX = len(PRODUCTS) + 1
IDENTIFIER_GENERATOR = itertools.count(START_INDEX)


@app.route(f'{BASE_URL}/products', methods=['GET'])
def read_many_products():
    products = list(PRODUCTS.values())

   # Retourne un tuple correspondant aux arguments du constructeur flask.Response
    # Cf : https://flask.palletsprojects.com/en/1.1.x/api/?highlight=response#flask.Response
    # Par défaut, le second argument est 200 (mais nous voulons être explicites lors de l'apprentissage des concepts).
    return jsonify(products), 200  # OK


@app.route(f'{BASE_URL}/products/<int:product_id>', methods=['GET'])
def read_one_product(product_id):
    product = PRODUCTS.get(product_id)

    if product is None:
        abort(404)

    return jsonify(product), 200  # OK


@app.route(f'{BASE_URL}/products/<int:product_id>', methods=['DELETE'])
def delete_one_product(product_id):
    product = PRODUCTS.pop(product_id, None)

    if product is None:
        abort(404)  # Aucun produit de product_id trouvé est une Erreur Non Trouvée (Not Found Error)

    # Si l'erreur est "204", le 1er argument (body) est ignoré
    # Nous pouvons mettre ce que nous voulons dans le premier argument (mais nous voulons être explicites pour rendre notre code plus maintenable).
    # '' ou None sont des valeurs couramment utilisées pour expliciter ce cas.
    #
    # L'action de suppression (méthode DELETE) n'a pas besoin de retourner l'entité puisque nous avons supprimé cette entité.
    return '', 204  # Pas de contenu


# Pas de product_id dans l'url de création (méthode POST) puisque c'est la base de données qui implémente le compteur d'id.
# Si les utilisateurs de l'api pouvaient choisir un id, cela conduirait à de nombreuses erreurs :
# - problème de compétition pour un id donné choisi par de nombreux utilisateurs.
# Comment savoir quel est l'id qui n'est pas utilisé pour le moment ?
# La base de données peut optimiser la gestion des id car elle sait comment ils sont créés.
@app.route(f'{BASE_URL}/products', methods=['POST'])
def create_one_product():
    data = request.get_json()

    if data is None:
        abort(400)  # L'absence de champ(s) nécessaire(s) est une Erreur de Requête Erronée (Bad Request Error)

    name = data.get('name')

    if name is None:
        abort(400)  # L'absence de champ nécessaire est une Erreur de Requête Erronée

    if name == '' or not isinstance(name, str):
        abort(422)  # Un mauvais format pour le champ requis est une Erreur d'Entité Non Traitable (Unprocessable Entity Error).

    next_id = next(IDENTIFIER_GENERATOR)
    PRODUCTS[next_id] = {'id' : next_id , 'name' : name }

    # Nous devons renvoyer l'entité entière pour communiquer le nouvel id à l'utilisateur de l'API.
    # De cette façon, il peut agir sur cette ressource en utilisant son id.
    #
    # Nous pourrions simplement retourner l'id, mais ce n'est pas dans l'esprit REST.
    # # N'oubliez pas : /<entity>/<entity_id> représente une entité entière.
    return jsonify(PRODUCTS[next_id]), 201  # Créé


@app.route(f'{BASE_URL}/products/<int:product_id>', methods=['PATCH'])
def update_one_product(product_id):
    data = request.get_json()
    if data is None:
        abort(400)

    name = data.get('name')

    if name is None:
        abort(400)

    if name == '' or not isinstance(name, str):
        abort(422)

    product = PRODUCTS.get(product_id)

    if product is None:
        abort(404)

    PRODUCTS[product_id]['name'] = name

    # Action de mise à jour (méthode UPDATE) pas besoin de retourner l'entité puisque nous savons ce que nous avons modifié.
    return '', 204