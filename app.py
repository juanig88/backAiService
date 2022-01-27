from products import products
from flask import Flask, jsonify, request
from flask_script import Manager, Server
import pypyodbc as podbc
import backAi
import nltk

app = Flask(__name__)



@app.route('/backAiService/products')
def getProducts():
    return jsonify({"products": products, "message": "Product's List!"})


@app.route('/backAiService/products/<string:product_name>')
def getProduct(product_name):
    productsFound = [
        product for product in products if product['name'] == product_name]
    if len(productsFound) > 0:
        return jsonify({"product": productsFound[0], "message": "Product found!"})
    return jsonify({"message": "Product NOT found"})


@app.route('/backAiService/products', methods=['POST'])
def addProduct():
    try:
        text = backAi.doBackAi(request.json['text'])
        return jsonify({"results": text})
    except (ValueError, KeyError, TypeError):
        return jsonify({"message": "Product NOT ADDED succesfully"})


@app.route('/backAiService/products/<string:product_name>', methods=['PUT'])
def editProduct(product_name):
    try:
        productsFound = [
            product for product in products if product['name'] == product_name]
        if len(productsFound) > 0:
            productsFound[0]['name'] = request.json['name']
            productsFound[0]['price'] = request.json['price']
            productsFound[0]['quantity'] = request.json['quantity']
            return jsonify({"message": "Product UPDATED succesfully", "products": productsFound[0]})
        return jsonify({"message": "Product not found"})
    except (ValueError, KeyError, TypeError):
        return jsonify({"message": "Product NOT UPDATED succesfully"})


@app.route('/backAiService/products/<string:product_name>', methods=['DELETE'])
def deleteProduct(product_name):
    try:
        productsFound = [
            product for product in products if product['name'] == product_name]
        if len(productsFound) > 0:
            print(productsFound)
            products.remove(productsFound[0])
            return jsonify({"message": "Product DELETED succesfully", "product": productsFound[0], "products": products})
        return jsonify({"message": "Product NOT found"})
    except (ValueError, KeyError, TypeError):
        return jsonify({"message": "Product NOT DELETED succesfully"})


def _run_on_start():
    backAi.populateTransformPrepositions()
    backAi.populateWordTokenDefinitive()


def run_server():
    _run_on_start()
    app.run(debug=True, use_reloader=False, port=4000)


if __name__ == '__main__':
    run_server()
