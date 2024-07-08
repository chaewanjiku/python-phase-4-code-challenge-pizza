#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify, abort
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)
api = Api(app)

@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

# Routes to retrieve restaurants
@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    restaurants = Restaurant.query.all()

    restaurant_list = [
        {
            "address": restaurant.address,
            "id": restaurant.id,
            "name": restaurant.name
        }
        for restaurant in restaurants
    ]

    return jsonify(restaurant_list), 200

@app.route('/restaurants/<int:id>', methods=['GET'])
def get_restaurant(id):
    restaurant = db.session.get(Restaurant, id)

    if restaurant is None:
        return jsonify({"error": "Restaurant not found"}), 404

    restaurant_dict = {
        "id": restaurant.id,
        "name": restaurant.name,
        "address": restaurant.address,
        "restaurant_pizzas": [
            {
                "id": restaurantpizza.id,
                "price": restaurantpizza.price,
                "pizza_id": restaurantpizza.pizza_id,
                "restaurant_id": restaurantpizza.restaurant_id,
                "pizza": {
                    "id": restaurantpizza.pizza.id,
                    "name": restaurantpizza.pizza.name,
                    "ingredients": restaurantpizza.pizza.ingredients
                }
            }
            for restaurantpizza in restaurant.restaurant_pizzas
        ]
    }

    return jsonify(restaurant_dict), 200



# Route to delete a restaurant
@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant(id):
    restaurant = Restaurant.query.get(id)

    if restaurant is None:
        return jsonify({"error": "Restaurant not found"}), 404

    db.session.delete(restaurant)
    db.session.commit()

    return jsonify({}), 204

# Route to retrieve pizzas
@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    pizzas = Pizza.query.all()

    pizza_list = [
        {
            "id": pizza.id,
            "ingredients": pizza.ingredients,
            "name": pizza.name
        }
        for pizza in pizzas
    ]

    return jsonify(pizza_list), 200

# Route to create a restaurant_pizza relationship
@app.route("/restaurant_pizzas", methods=["POST"])
@app.route("/restaurant_pizzas", methods=["POST"])
def create_restaurant_pizza():
    data = request.get_json()
    price = data.get("price")
    pizza_id = data.get("pizza_id")
    restaurant_id = data.get("restaurant_id")

    if price < 1 or price > 30:
        return jsonify({"errors": ["validation errors"]}), 400

    try:
        new_restaurant_pizza = RestaurantPizza(price=price, pizza_id=pizza_id, restaurant_id=restaurant_id)
        db.session.add(new_restaurant_pizza)
        db.session.commit()
        return jsonify(new_restaurant_pizza.to_dict()), 201
    except Exception as e:
        return jsonify({"error": "Internal Server Error"}), 500
if __name__ == "__main__":
    app.run(port=5555, debug=True)
