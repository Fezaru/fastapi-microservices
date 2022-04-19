from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis_om import get_redis_connection, HashModel

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_methods=['*'],
    allow_headers=['*'],
)

redis = get_redis_connection(
    host='redis-17901.c293.eu-central-1-1.ec2.cloud.redislabs.com',
    port='17901',
    password='0TxKoNjSXwISEVUZmHZsEp8QV5jHjycS',
    decode_responses=True
)


class Product(HashModel):
    name: str
    price: int
    quantity: int

    class Meta:
        database = redis


def format_products(pk: str):
    product = Product.get(pk)

    return {'id': product.pk, 'name': product.name, 'price': product.price, 'quantity': product.quantity}


@app.get('/products')
def list_products():
    return [format_products(pk) for pk in Product.all_pks()]


@app.post('/products')
def create_product(product: Product):
    return product.save()


@app.get('/products/{pk}')
def get_product(pk: str):
    return Product.get(pk)


@app.delete('/products/{pk}')
def delete_product(pk: str):
    return Product.delete(pk)
