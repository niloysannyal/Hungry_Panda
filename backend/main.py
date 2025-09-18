import uvicorn
from fastapi import FastAPI
from fastapi import Request
from starlette.responses import JSONResponse
import db_helper
import generic_helper
from backend.generic_helper import get_str_from_food_dict

app = FastAPI()


food_menu = {
    "Burgers": ["Chicken Burger", "Cheese Burger", "Veggie Burger"],
    "Pizzas": ["Meat Lover's Pizza", "Pepperoni Pizza", "BBQ Chicken Pizza"],
    "Sides": ["French Fries", "Onion Rings"],
    "Drinks": ["Coca-Cola", "Sprite", "Water"],
    "Desserts": ["Ice Cream", "Brownie"],
    "Combos": ["The Hunger Buster", "Pizza Lovers' Duo", "Happy Ending Combo"]
}


# Orders by session_id
inprogress_orders = {}


@app.post("/")
async def handle_request(request: Request):
    #Retrieve the JSON data from the request
    payload = await request.json()

    #Extract necessary information from the payload
    #Based on the structure of the WebhookRequest from Dialogflow
    intent = payload["queryResult"]["intent"]["displayName"]
    parameters = payload["queryResult"]["parameters"]
    output_contexts = payload["queryResult"]["outputContexts"]
    session_id = generic_helper.extract_session_id(output_contexts[0]["name"])

    intend_handler_dict = {
        "new.order": initialize_order,
        "order.add - context: ongoing-order": add_to_order,
        "order.remove - context: ongoing-order": remove_from_order,
        "order.complete - context: ongoing-order": complete_order,
        "track.order - context: ongoing-tracking": track_order
    }

    return intend_handler_dict[intent](parameters, session_id)




def initialize_order(parameters, session_id):
    # Start a new empty order for this session
    inprogress_orders[session_id] = {}

    print(f"New order initialized for session: {session_id}")

    fulfillment_text = "Great! Starting a new order. What would you like to have? We’ve got 🍔 Burgers | 🍕 Pizza | 🍟 Sides | 🥤 Drinks | 🍦 Desserts | 🍽️ Combos"

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })





def add_to_order(parameters: dict, session_id: str):
    food_items = parameters["food-item"]
    quantities = parameters["number"]

    if len(food_items) != len(quantities):
        fulfillment_text = "Sorry I didn't understand. Can you please specify food items and quantities clearly?"
    else:
        new_food_dict = dict(zip(food_items, quantities))
        if session_id in inprogress_orders:
            current_food_dict = inprogress_orders[session_id]
            for item, qty in new_food_dict.items():
                if item in current_food_dict:
                    current_food_dict[item] += qty
                else:
                    current_food_dict[item] = qty
            inprogress_orders[session_id] = current_food_dict
        else:
            inprogress_orders[session_id] = new_food_dict

        print("*"*50)
        print(session_id, inprogress_orders[session_id])

        order_update = generic_helper.get_str_from_food_dict(inprogress_orders[session_id])

        # current_order = {"Chicken Burger": 2, "French Fries": 2}
        current_order = inprogress_orders[session_id]
        chosen_categories = set()
        foods = current_order.keys()
        for food in foods:
            for key in food_menu.keys():
                if food in set(food_menu[key]):
                    chosen_categories.add(key)
                    break
        suggestions = [cat for cat in food_menu.keys() if cat not in chosen_categories]
        print(suggestions)

        if suggestions:
            fulfillment_text = f"Items added. So far you have {order_update}. Anything else? Maybe you'd like something from our {', '.join(suggestions)} menu."
        else:
            fulfillment_text = f"Items added. So far you have {order_update}. Anything else you want to order?"

        suggestions.clear()

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })





def remove_from_order(parameters: dict, session_id: str):
    if session_id not in inprogress_orders:
        return JSONResponse(content={
            "fulfillmentText": "Sorry, I'm having some issue finding your order. Can you please place a new order?"
        })

    current_order = inprogress_orders[session_id]
    food_items = parameters.get("food-item", [])
    quantities = parameters.get("number", [])

    # Normalize food_items to list if single string
    if isinstance(food_items, str):
        food_items = [food_items]

    # Normalize quantities to list
    if isinstance(quantities, (str, int, float)):
        try:
            quantities = [float(quantities)]
        except:
            quantities = [None]  # If parsing fails, remove entire item
    elif isinstance(quantities, list):
        # Convert each element to float if possible
        for i in range(len(quantities)):
            try:
                quantities[i] = float(quantities[i])
            except:
                quantities[i] = None

    # Pad missing quantities with None
    while len(quantities) < len(food_items):
        quantities.append(None)  # Means remove entirely

    removed_items = {}
    no_such_items = []

    for item, qty in zip(food_items, quantities):
        if item not in current_order:
            no_such_items.append(item)
        else:
            if qty is None:  # No number mentioned → remove entire item
                removed_items[item] = current_order[item]
                del current_order[item]
            else:  # Partial removal
                if current_order[item] - qty <= 0:
                    removed_items[item] = current_order[item]
                    del current_order[item]
                else:
                    removed_items[item] = qty
                    current_order[item] -= qty

    # Build response
    fulfillment_text = ""
    if removed_items:
        fulfillment_text += f"Removed {generic_helper.get_str_from_food_dict(removed_items)} from your order. "
    if no_such_items:
        fulfillment_text += f"Your current order doesn't have {', '.join(no_such_items)}. "

    if not current_order:
        fulfillment_text += "Your order is empty!"
    else:
        order_update = generic_helper.get_str_from_food_dict(current_order)
        fulfillment_text += f"Your remaining order: {order_update}. Anything else?"

    return JSONResponse(
        content={"fulfillmentText": fulfillment_text}
    )





def complete_order(parameters: dict, session_id: str):
    if session_id not in inprogress_orders:
        fulfillment_text = "Sorry! I'm having a trouble finding your order. Can you please place a new order?"
    else:
        order = inprogress_orders[session_id]
        order_id = save_to_db(order)

    if order_id == -1:
        return ""
    else:
        order_total = db_helper.get_total_order_price(order_id)
        fulfillment_text = f"🎉 Awesome! Your order has been placed. \nYour order ID is #{order_id}. \nTotal: {order_total}TK which you can pay at the time of delivery!"

    del inprogress_orders[session_id]

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })




def save_to_db(order: dict):

    next_order_id = db_helper.get_next_order_id()

    for item, quantity in order.items():
        return_code = db_helper.insert_order_item(
            item,
            quantity,
            next_order_id
        )

        if return_code == -1:
            return -1

    db_helper.insert_order_tracking(next_order_id, "preparing")

    return next_order_id



def track_order(parameters: dict, session_id: str):
    order_id = int(parameters["number"])
    order_status = db_helper.get_order_status(order_id)

    if order_status == 'preparing':
        fulfillment_text = f"🧑‍🍳 Your order #{order_id} is being prepared."
    elif order_status == 'in transit':
        fulfillment_text = f"🚗 Your order #{order_id} is out for delivery."
    elif order_status == 'delivered':
        fulfillment_text = f"✅ Your order #{order_id} has been delivered. Enjoy your meal!"
    else:
        fulfillment_text = f"No order found for {order_id}. Please check your order id and try again."

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)