import time

from fastapi import FastAPI
from fastapi.background import BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from redis_om import get_redis_connection, HashModel
from starlette.requests import Request
import requests

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_methods=['*'],
    allow_headers=['*'],
)

# Needs to be separate, 1 microservice = 1 or more database
redis = get_redis_connection(
    host='redis-17901.c293.eu-central-1-1.ec2.cloud.redislabs.com',
    port='17901',
    password='0TxKoNjSXwISEVUZmHZsEp8QV5jHjycS',
    decode_responses=True
)


class Order(HashModel):
    product_id: str
    price: float
    fee: float
    total: float
    quantity: int
    status: str

    class Meta:
        database = redis


@app.get('/orders')
async def list_orders():
    return Order.all_pks()


@app.get('/orders/{pk}')
async def list_orders(pk: str):
    return Order.get(pk)


@app.post('/orders')
async def create_order(request: Request, background_tasks: BackgroundTasks):  # id, quantity
    body = await request.json()

    response = requests.get(f'http://localhost:8000/products/{body.get("id")}')
    product = response.json()
    order = Order(
        product_id=body.get('id'),
        price=product.get('price'),
        fee=.2 * product.get('price'),
        total=1.2 * product.get('price'),
        quantity=body.get('quantity'),
        status='pending',
    )
    order.save()

    background_tasks.add_task(process_order, order)

    return order


def process_order(order: Order):
    time.sleep(5)
    order.status = 'completed'
    redis.xadd('order_completed', order.dict(), '*')
    return order.save()
