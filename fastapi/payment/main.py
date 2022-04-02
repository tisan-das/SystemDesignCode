from math import prod
from typing import Optional

from fastapi import BackgroundTasks, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from redis_om import get_redis_connection,HashModel
from pydantic import BaseModel
import requests, time

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

class Order(HashModel):
    product_id: str
    price: float
    fee: float
    total: float
    quantity: int
    status: str # pending/completed/refunds

    class Meta:
        database = redis

class BaseRequest(BaseModel):
    product_id: str
    quantity: int

@app.post("/order")
async def create(orderRequest: BaseRequest, backgroundTasks:BackgroundTasks):
    req = requests.get("http://localhost:8000/product/"+str(orderRequest.product_id))
    req = req.json()

    if len(req)==0:
        return {"error":"Product ID not found!"}
    try:
        order = Order(
            product_id = req["id"],
            price = req["price"],
            fee = 0.2* req["price"],
            total = 1.2* req["price"]* orderRequest.quantity,
            quantity = orderRequest.quantity,
            status = "pending"
        )
        order.save()
        backgroundTasks.add_task(order_completed, order)
        # order_completed(order)
        return order
    except Exception as ex:
        print("Got exception during creating order: "+str(ex))
        return {"error": str(ex)}

def order_completed(order: Order):
    time.sleep(10)
    order.status = "completed"
    redis.xadd("order_completed", order.dict(), "*")
    order.save()


@app.get("/order/{order_id}")
def get_order(order_id: str):
    return Order.get(order_id)

