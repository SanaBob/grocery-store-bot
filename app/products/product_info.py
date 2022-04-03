from app.database import MOCK_PRODUCT_DATA
import re
from app.products.base_handler import BaseHandler
import wikipedia
from googletrans import Translator

class ProductInfoHandler(BaseHandler):
    """
    A class used to represent a mini-bot to handle product queries.
    """

    CONSTANT_NUTRITION = ["calories", "calorie", "protein", "carbs", "carbohydrates", "sugar", "fat", "nutrition"]
    CONSTANT_LANGUAGES = ['ab','aa','af','ak','sq','am','ar','an','hy','as','av','ae','ay','az','bm','ba','eu','be','bn','bh','bi','bs','br','bg','my','ca','km','ch','ce','ny','zh','cu','cv','kw','co','cr','hr','cs','da','dv','nl','dz','en','eo','et','ee','fo','fj','fi','fr','ff','gd','gl','lg','ka','de','ki','el','kl','gn','gu','ht','ha','he','hz','hi','ho','hu','is','io','ig','id','ia','ie','iu','ik','ga','it','ja','jv','kn','kr','ks','kk','rw','kv','kg','ko','kj','ku','ky','lo','la','lv','lb','li','ln','lt','lu','mk','mg','ms','ml','mt','gv','mi','mr','mh','ro','mn','na','nv','nd','ng','ne','se','no','nb','nn','ii','oc','oj','or','om','os','pi','pa','ps','fa','pl','pt','qu','rm','rn','ru','sm','sg','sa','sc','sr','sn','sd','si','sk','sl','so','st','nr','es','su','sw','ss','sv','tl','ty','tg','ta','tt','te','th','bo','ti','to','ts','tn','tr','tk','tw','ug','uk','ur','uz','ve','vi','vo','wa','cy','fy','wo','xh','yi','yo','za','zu']
    translator = Translator()

    def __init__(self) -> None:
        super().__init__()

    def create_match_paterns(self):
        # Product-related patterns
        self.price_pattern = re.compile(
            r"(price|cost|how much|money)", re.IGNORECASE)
        self.stock_pattern = re.compile(r"(stock|how many|amount)", re.IGNORECASE)
        self.nutrition_pattern = re.compile(
            r"(calories|protein|carbs|carbohydrates|sugar|fat|nutrition|nutritional|weight|health|healthy)", re.IGNORECASE)
        self.definition_pattern = re.compile(
            r"(definition|exactly)", re.IGNORECASE)

    def dispose(self):
        super().dispose()

    def handle_prod_intent(self, product: str, intent: str) -> str:
        
        intent = intent.split("-")[1] # hardcoded to filter intent: product-<intent> Ex. product-price -> intent = price

        request = None

        cursor = self.db.execute_query(
            "SELECT product.id FROM product WHERE product.name = ? OR product.names = ?", 
                params=tuple([product, product]))
        data = cursor.fetchone()
        if (not data):
            return None
        
        request = {"request": intent, "id": data[0]}

        return self.handle_product_info(None, **request)

    def handle(self, message: str, intent=None) -> str: # if 2 args => message = product_name
        if intent is not None:
            return self.handle_prod_intent(message, intent)

        # Call parser
        kwargs = self.parse(message=message)

        # If there is a topic detected, we find the response
        # By calling the handler with the message (for convenience) and its necessary arguments
        response = None
        if kwargs:
            response = self.handle_product_info(message, **kwargs)

            return response

    def parse(self, message: str) -> dict:
        request = None

        # Check for keywords for prices
        if self.definition_pattern.search(message):
            request = "definition"
        elif self.nutrition_pattern.search(message):
            request = "nutrition"
        elif self.price_pattern.search(message):
            request = "price"
        elif self.stock_pattern.search(message):
            request = "stock"

        # If the request is truly about product
        if request:
            id = None
            for prod in MOCK_PRODUCT_DATA:
                prod_name = prod["name"]
                prod_id = prod["id"]
                prod_names = prod["names"]

                if prod_name in message or prod_id in message or prod_names in message:
                    id = prod["id"]

        return {"request": request, "id": id} if request else None

    def handle_product_info(self, message=None, **kwargs) -> str:
        # kwargs are arguments such as product_name, price, operators (<. >)
        # This really depends on how you define your parser
        prod_id = kwargs["id"]

        # Get the product information
        products = self.db.get_product("id", prod_id)
        # Since id is unique, we can assume there is only one product
        if products:
            product = products[0]

        reply = None

        prod_msg_type = kwargs.get("request")
        if prod_msg_type == "price":
            reply = "%s cost $%s %s." % (
                product['names'].capitalize(), product['price'], product['price_scale'])
        elif prod_msg_type == "stock":
            if product['in_stock']:
                reply = "%s are in stock." % (product['names'].capitalize())
            else:
                reply = "%s are out of stock." % (
                    product['names'].capitalize())
        elif prod_msg_type == "definition":
            for word in message.replace("?", " ").split(" "):
                if word.lower() in self.CONSTANT_NUTRITION:
                    reply = wikipedia.summary(word.lower(), sentences=1)
        elif prod_msg_type == "nutrition":
            reply = "%s Nutrition Facts: Calories = %s, Protein = %s, Carbs = %s, Sugar = %s, Fat = %s." % (
                product['name'].capitalize(), product['calories'], product['protein'], product['carbs'], product['sugar'], product['fat'])
        
        if message.split(" ")[0].lower() in self.CONSTANT_LANGUAGES:
            try:
                reply = self.translator.translate(reply, src="en", dest=message.split(" ")[0]).text
            except:
                pass

        return reply