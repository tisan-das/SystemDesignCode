from main import Product, redis
import time

key = "order_completed"
group = "inventory_group"

try:
    redis.xgroup_create(key,group)
except:
    print("Group already exists!")

while True:
    try:
        results = redis.xreadgroup(group, key, {key: ">"}, None)
        if len(results)>0:
            for result in results:
                print("got entries: "+str(result))
                for row in result[1]:
                    obj = row[1]
                    try:
                        product = Product.get(obj["product_id"])
                        product.quantity -= obj["quantity"]
                        product.save()
                    except Exception as ex:
                        redis.xadd('refund_order', obj, "*")
    except Exception as ex:
        print(str(ex))
    time.sleep(20)