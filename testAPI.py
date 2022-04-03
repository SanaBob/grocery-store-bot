from app.products.product_info import ProductInfoHandler

StoreHandler = ProductInfoHandler()
message = "What is the definition of calories?"
output = StoreHandler.handle(message)
print(output)

StoreHandler = ProductInfoHandler()
message = "What is the definition of carbohydrates?"
output = StoreHandler.handle(message)
print(output)

# StoreHandler = ProductInfoHandler()
# message = "fr What is the definition of calories?"
# output = StoreHandler.handle(message)
# print(output)

# StoreHandler = ProductInfoHandler()
# message = "sv What is the definition of calories?"
# output = StoreHandler.handle(message)
# print(output)