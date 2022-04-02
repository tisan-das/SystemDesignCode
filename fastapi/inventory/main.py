from math import prod
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis_om import get_redis_connection,HashModel


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods = ["*"],
    allow_headers = ["*"]
)

redis = get_redis_connection(
        host = "redis-14283.c264.ap-south-1-1.ec2.cloud.redislabs.com",
        port = "14283",
        password = "1BXD4Go43THJLaRZ7iKXUwKj6s2tPSt8",
        decode_responses = True
    )


class Product(HashModel):
    name: str
    price: float
    quantity: int

    class Meta:
        database = redis

def format(pk: str):
    try:
        product = Product.get(pk)
        return {
            "id": product.pk,
            "name": product.name,
            "price": product.price,
            "quantity": product.quantity
        }
    except Exception as ex:
        return {}

@app.get("/products")
def fetch_all():
    return [format(pk) for pk in Product.all_pks()]

@app.get("/product/{item_id}")
def fetch_item(item_id:str):
    return format(item_id)

@app.post("/product")
def add_item(product: Product):
    return product.save()

@app.delete("/product/{item_id}")
def remove_item(item_id: str):
    return Product.delete(item_id)
