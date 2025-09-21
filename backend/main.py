import uvicorn
from fastapi import FastAPI, Request
from starlette.responses import JSONResponse
from . import db_helper
from . import generic_helper
from .generic_helper import get_str_from_food_dict

app = FastAPI()

food_menu = {
    "Burgers": [
        {"name": "Chicken Burger", "price": 299},
        {"name": "Cheese Burger", "price": 250},
        {"name": "Veggie Burger", "price": 220}
    ],
    "Pizzas": [
        {"name": "Meat Lover's Pizza", "price": 890},
        {"name": "Pepperoni Pizza", "price": 720},
        {"name": "BBQ Chicken Pizza", "price": 690}
    ],
    "Sides": [
        {"name": "French Fries", "price": 120},
        {"name": "Onion Rings", "price": 150}
    ],
    "Drinks": [
        {"name": "Coca-Cola", "price": 40},
        {"name": "Sprite", "price": 40},
        {"name": "Water", "price": 20}
    ],
    "Desserts": [
        {"name": "Ice Cream", "price": 100},
        {"name": "Brownie", "price": 100}
    ],
    "Combos": [
        {"name": "The Hunger Buster", "price": 450},
        {"name": "Pizza Lover's Duo", "price": 1250},
        {"name": "Happy Ending Combo", "price": 950}
    ]
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
        "order.pizzas": handle_category_menu,
        "order.burgers": handle_category_menu,
        "order.sides": handle_category_menu,
        "order.drinks": handle_category_menu,
        "order.desserts": handle_category_menu,
        "order.combos": handle_category_menu,
        "order.add - context: ongoing-order": add_to_order,
        "order.remove - context: ongoing-order": remove_from_order,
        "order.complete - context: ongoing-order": complete_order,
        "order.complete - confirmation": complete_order,
        "track.order - context: ongoing-tracking": track_order
    }

    handler = intend_handler_dict.get(intent)
    if handler:
        return handler(parameters, session_id)
    else:
        print(f"Unhandled intent: {intent}")  # Debug print
        return JSONResponse(content={"fulfillmentText": "Sorry, I didn't understand that."})




def initialize_order(parameters, session_id):
    # Start a new empty order for this session
    inprogress_orders[session_id] = {}

    print(f"New order initialized for session: {session_id}")

    fulfillment_text = "Great! Starting a new order. What would you like to have? We’ve got 🍔 Burgers | 🍕 Pizza | 🍟 Sides | 🥤 Drinks | 🍦 Desserts | 🍽️ Combos"

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })



def handle_category_menu(parameters, session_id):
    category_name = parameters["category"].capitalize()

    if category_name == "Burgers":
        icon = "🍔"
    elif category_name == "Pizzas":
        icon = "🍕"
    elif category_name == "Sides":
        icon = "🍟"
    elif category_name == "Drinks":
        icon = "🥤"
    elif category_name == "Desserts":
        icon = "🍦"
    else:
        icon = "🍽️"

    items = food_menu.get(category_name, [])
    if not items:
        return JSONResponse(content={
            "fulfillmentMessages": [
                {"text": {"text": [f"Sorry, we don't have items for {category_name}."]}}
            ]
        })

    # Create a list of separate lines as separate messages
    messages = [{"text": {"text": [f"{icon} Here’s our {category_name} menu:"]}}]

    count = 1
    for item in items:
        messages.append({"text": {"text": [f"{count}. {item['name']} – {item['price']} BDT"]}})
        count += 1

    messages.append({"text": {"text": ["Which would you like to order?"]}})

    return JSONResponse(content={"fulfillmentMessages": messages})





def get_price_from_menu(item_name):
    for category_items in food_menu.values():
        for item in category_items:
            if item["name"] == item_name:
                return item["price"]
    return 0  # fallback if item not found





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

        order_update = generic_helper.get_str_from_food_dict(inprogress_orders[session_id])

        # Calculate total
        current_total = 0
        for food, qty in inprogress_orders[session_id].items():
            price = get_price_from_menu(food)
            current_total += price * qty

        print(session_id, inprogress_orders[session_id], current_total)

        # Suggest categories not yet ordered
        current_order = inprogress_orders[session_id]
        chosen_categories = set()
        for food in current_order.keys():
            for key, items in food_menu.items():
                if any(item["name"] == food for item in items):
                    chosen_categories.add(key)
                    break
        suggestions = [cat for cat in food_menu.keys() if cat not in chosen_categories]

        if suggestions:
            fulfillment_text = f"Items added. So far you have {order_update}. Total: {int(current_total)} BDT. Anything else? Maybe you'd like something from our {', '.join(suggestions)} menu."
        else:
            fulfillment_text = f"Items added. So far you have {order_update}. Total: {int(current_total)} BDT. Anything else you want to order?"

        suggestions.clear()

    return JSONResponse(content={"fulfillmentText": fulfillment_text})





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
        return JSONResponse(content={
            "fulfillmentText": "Sorry! I can't find any ongoing order. Please start a new one."
        })

    order = inprogress_orders[session_id]
    confirmation = parameters.get("confirmation")

    # Step 1: If no confirmation yet → summarize & ask
    if not confirmation:
        order_summary = ", ".join([f"{int(qty)} {item}" for item, qty in order.items()])
        order_total = sum(
            int(qty) * next(
                (food["price"] for category in food_menu.values() for food in category if food["name"] == item),
                0
            )
            for item, qty in order.items()
        )

        fulfillment_text = (
            f"✅ You have {order_summary}.\n"
            f"Total: {order_total} BDT.\n"
            f"Do you want to confirm your order?"
        )
        return JSONResponse(content={"fulfillmentText": fulfillment_text})

    # Step 2: If confirmation provided → act accordingly
    confirmation = confirmation.lower()

    if confirmation in ["yes", "y", "yep", "sure", "ok", "okay"]:
        order_id = save_to_db(order)
        if order_id == -1:
            return JSONResponse(content={"fulfillmentText": "⚠️ Oops! Something went wrong saving your order."})

        order_total = db_helper.get_total_order_price(order_id)
        fulfillment_text = (
            f"🎉 Awesome! Your order has been placed.\n"
            f"Order ID: #{order_id}\n"
            f"Total: {int(order_total)} BDT. You can pay at delivery!"
        )
        del inprogress_orders[session_id]

    else:  # Negative confirmation
        fulfillment_text = (
            "❌ Okay, I won’t place the order yet.\n"
            "👉 You can Add or Remove items from your order.\n"
            "Or, start a fresh order anytime by saying New Order."
        )
        # Notice: We do NOT delete the order here. User can continue editing.

    return JSONResponse(content={"fulfillmentText": fulfillment_text})





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

    db_helper.insert_order_tracking(next_order_id, "processing")

    return next_order_id




def track_order(parameters: dict, session_id: str):
    order_id = int(parameters["number"])
    order_status = db_helper.get_order_status(order_id)

    if order_status == 'processing':
        fulfillment_text = f"🧑‍🍳 Your order #{order_id} is processing"
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
