# 🐼 Panda Bot – Hungry Panda Food Ordering Chatbot

**Panda Bot** is an AI-powered chatbot designed to provide a seamless and interactive food ordering experience for the **Hungry Panda** website. Users can browse menus, add or remove items, and place orders directly via conversational interactions powered by **Dialogflow** and **FastAPI**.  

---

## 🌟 Table of Contents

- [🍴 Project Overview](#-project-overview)
- [✨ Features](#-features)
- [🛠️ Technologies Used](#-technologies-used)
- [📁 Folder Structure](#-folder-structure)
- [⚡ Installation](#-installation)
- [🚀 Usage](#-usage)
- [📡 API Endpoints](#-api-endpoints)
- [🔮 Future Enhancements](#-future-enhancements)
- [🤝 Contributing](#-contributing)
- [📞 Contact](#-contact)
- [📄 License](#-license)
- [🙏 Acknowledgements](#-acknowledgements)

---

## 🍴 Project Overview

**Panda Bot** enables users to interact with **Hungry Panda** naturally:

- 🍔 Browse **Burgers**, 🍕 **Pizzas**, 🍟 **Sides**, 🥤 **Drinks**, 🍦 **Desserts**, and 🍽️ **Combos**.  
- ➕ Add or ➖ remove items from the order.  
- 💰 See running totals and order summaries in real-time.  
- ✅ Confirm and place orders with backend persistence in **MySQL**.  
- 🚚 Track order status: **processing**, **in transit**, **delivered**.  

The chatbot provides a friendly and engaging ordering experience with emojis and structured responses for clarity.

---

## ✨ Features

- **📜 Full Menu Browsing** – View all items with prices.  
- **📂 Category-wise Browsing** – Focus on specific categories like Pizzas or Burgers.  
- **➕ Add / ➖ Remove Items** – Dynamically modify ongoing orders.  
- **🧾 Order Confirmation** – Confirm orders via natural conversation.  
- **🚦 Order Tracking** – Check status by Order ID.  
- **😃 Friendly UI** – Emojis and clear messages enhance readability.  

---

## 🛠️ Technologies Used

- **Backend:** Python, FastAPI  
- **Frontend:** HTML, CSS (`frontend/index.html`)  
- **Database:** MySQL (via `db_helper.py`)  
- **Dialogflow:** Intent-based conversational AI  
- **Ngrok:** Local server tunneling for webhook integration  
- **Python Packages:** See `requirements.txt`  

---

## 📁 Folder Structure
```
Hungry_Panda/
│
├── dialogflow_assets/
│   └── training_samples.txt   # Dialogflow training phrases
│
├── frontend/
│   ├── images/                # Menu and UI images
│   └── index.html             # Landing page
│
├── backend/
│   ├── main.py                # FastAPI backend logic
│   ├── generic_helper.py      # Utility helper functions
│   └── db_helper.py           # Database helper functions
│
├── ngrok.exe                  # Ngrok for webhook tunneling
├── README.md                  # Project documentation
└── requirements.txt           # Python dependencies
```


---

## ⚡ Installation

1. **Clone the repository:**

```bash
git clone https://github.com/yourusername/Hungry_Panda.git
cd Hungry_Panda
```
2. **Install dependencies:**
```
pip install -r requirements.txt
```
3. **Configure database connection in backend/db_helper.py:**
```
MYSQLHOST=
MYSQLUSER=
MYSQLPASSWORD=
MYSQLDATABASE=
MYSQLPORT=
```
4. **Run FastAPI backend:**
```
python backend/main.py
```
5. **Expose webhook via Ngrok (for Dialogflow integration):**
```
ngrok http 8000
```

## 🚀 Usage

Follow these steps to interact with **Panda Bot** and place orders on **Hungry Panda**.

### 1️⃣ Start a New Order

To begin ordering, start a new session:
```
User: New order
Bot:  🐼 Great! Starting a new order. What would you like to have?
We’ve got 🍔 Burgers | 🍕 Pizzas | 🍟 Sides | 🥤 Drinks | 🍦 Desserts | 🍽️ Combos |
Or, you can see our full menu.
```

### 2️⃣ Browse the Menu

You can view either a full menu or a specific category.

#### a) Full Menu

```
User: Show me the full menu
Bot: 🐼 Here’s the full Hungry Panda menu:
    🍔 Burgers:
    1. Chicken Burger – 299 BDT
    2. Cheese Burger – 250 BDT
    3. Veggie Burger – 220 BDT

    🍕 Pizzas:
    1. Meat Lover's Pizza – 890 BDT
    2. Pepperoni Pizza – 720 BDT
    3. BBQ Chicken Pizza – 690 BDT

    🍟 Sides:
    1. French Fries – 120 BDT
    2. Onion Rings – 150 BDT

    🥤 Drinks:
    1. Coca-Cola – 40 BDT
    2. Sprite – 40 BDT
    3. Water – 20 BDT

    🍦 Desserts:
    1. Ice Cream – 100 BDT
    2. Brownie – 100 BDT

    🍽️ Combos:
    1. The Hunger Buster – 450 BDT
    2. Pizza Lover's Duo – 1250 BDT
    3. Happy Ending Combo – 950 BDT

    You can place an order by mentioning quantity before item name.
```

#### b) Category Menu
```
User: Show me Pizzas
Bot: 🍕 Here’s our Pizzas menu:
    1. Meat Lover's Pizza – 890 BDT
    2. Pepperoni Pizza – 720 BDT
    3. BBQ Chicken Pizza – 690 BDT
    Which would you like to order?
```


### 3️⃣ Add Items to Your Order

You can add one or multiple items with quantities:
```
User: Add 2 Pepperoni Pizza and 2 French Fries
Bot: Items added. So far you have 2 Pepperoni Pizza, 2 French Fries. Total: 1680 BDT. Anything else?
    Maybe you'd like something from our Burgers, Drinks, Desserts, Combos menu.
```

### 4️⃣ Remove Items from Your Order

Remove items entirely or partially:
```
User: Remove 1 Pepperoni Pizza
Bot: Removed 1 Pepperoni Pizza. Your remaining order: 1 Pepperoni Pizza, 2 French Fries. Anything else?
User: Remove French Fries
Bot: Removed 2 French Fries. Your remaining order: 1 Pepperoni Pizza. Anything else?
```

### 5️⃣ Confirm Your Order

After adding all items, confirm the order:
```
User: That's all I wanted
Bot: ✅ You have 1 Pepperoni Pizza. Total: 720 BDT. Do you want to confirm your order?
User: Yes
Bot: 🎉 Awesome! Your order has been placed. Order ID: #1022 Total: 720 BDT. You can pay at delivery!
```

If you reply **No**, the bot will allow you to continue editing your order.


### 6️⃣ Track Order Status

Check the status of an existing order by Order ID:
```
User: I am very hungry. Please track my order
Bot: Can you give me your tracking ID? I’ll check the order status right away
User: It's 1022
Bot Responses: 🧑‍🍳 Your order #1022 is processing
               🚗 Your order #1022 is out for delivery
               ✅ Your order #1022 has been delivered. Enjoy your meal!
```
If the Order ID is invalid:
```
Bot: No order found for #1022. Please check your order ID and try again.
```


### 7️⃣ Quick Tips

- Use **full names** of menu items exactly as listed. Also, usual little typos are handled.   
- Mention **quantity before the item name**: `"Add 2 Pepperoni Pizza"`  
- You can **switch categories anytime** by typing the category name.  
- **Start a new order** anytime by saying `"New order"`.  
- The bot keeps track of **current totals** and **suggests remaining categories**.

**🍽️ Enjoy ordering with Panda Bot – making Hungry Panda a fun and interactive experience!**

---

## 📡 API Endpoints

| Endpoint                 | Method | Description                                           |
|--------------------------|--------|-------------------------------------------------------|
| `/`                      | POST   | Dialogflow webhook handling **all intents**.         |
| `/initialize_order`       | POST   | Starts a **new order session** for the user.         |
| `/add_to_order`           | POST   | Adds **items** to the ongoing order.                |
| `/remove_from_order`      | POST   | Removes **items** from the ongoing order.           |
| `/complete_order`         | POST   | Confirms and **saves the order** to the database.   |
| `/track_order`            | POST   | Checks **order status** by Order ID.                |

> 💡 **Note:** All endpoints accept JSON requests and respond with fulfillment messages suitable for Dialogflow chatbot integration.

---

## 🚀 Future Enhancements

We are planning several improvements to make **Hungry Panda** even more user-friendly and robust:

- **Payment Integration** 💳  
  Add support for **online payments** via BKash, Nagad, or local payment gateways for a seamless checkout experience.

- **User Accounts & History** 🧑‍🍳  
  Enable users to **create accounts**, view their **order history**, and repeat past orders quickly.

- **Real-time Order Tracking** 🚗  
  Provide a **live tracking interface** showing the exact status of the order from kitchen to delivery.

- **Multi-language Support** 🌐  
  Expand the chatbot to support **multiple languages** for a wider audience.

- **Promotions & Discounts** 🎁  
  Implement **discount codes, coupons, and special offers** to enhance customer engagement.

- **Recommendation System** 🤖  
  Suggest items based on **past orders, popularity, and combos** to improve sales and user experience.

- **Voice Interaction** 🎤  
  Integrate **voice commands** to allow users to place orders using speech through the chatbot.


---

## 🧩 Contributing

We welcome contributions to make **Hungry Panda** better!  

1. Fork the repository.  
2. Create a new branch (`git checkout -b feature-name`).  
3. Commit your changes (`git commit -m 'Add new feature'`).  
4. Push to the branch (`git push origin feature-name`).  
5. Create a **Pull Request** for review.  

> 📌 Please ensure that all new features are compatible with the existing Dialogflow intents and database schema.

---

## 📞 Contact

For any queries or support, contact:  

- **Niloy Sannyal**  
- 📧 Email: niloysannyal@gmail.com  
- 📱 Mobile: +8801783445245  
- 🌐 GitHub: [https://github.com/niloysannyal](https://github.com/niloysannyal)  

---

## 📝 License

This project is licensed under the **MIT License**.  
See the [LICENSE](LICENSE) file for details.  

---

## 🎉 Acknowledgements

- Thanks to **Dialogflow** for providing an easy-to-use NLP platform.  
- Inspired by modern **food delivery apps** for creating a seamless chatbot experience.  
- Special thanks to **FastAPI** and **Ngrok** teams for enabling rapid development and testing.  
- Credit to **Dhaval Patel** and **Codebasics YouTube channel** for tutorials and guidance that helped in building this project.
