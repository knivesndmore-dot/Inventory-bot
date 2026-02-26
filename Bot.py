from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import json, os

TOKEN = os.getenv("TOKEN")
OWNER_ID = 7153152247

# ---------------- STOCK ----------------
STOCK_FILE = "stock.json"

def load_stock():
    if not os.path.exists(STOCK_FILE):
        return {}
    return json.load(open(STOCK_FILE))

def save_stock(data):
    json.dump(data, open(STOCK_FILE,"w"))

def is_owner(update):
    return update.effective_user.id == OWNER_ID

# ADD ITEM
async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update): return
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /add item qty")
        return
    item = context.args[0]
    try:
        qty = int(context.args[1])
    except:
        await update.message.reply_text("Quantity must be number")
        return

    stock = load_stock()
    stock[item] = stock.get(item,0)+qty
    save_stock(stock)
    await update.message.reply_text(f"{item} added. Total: {stock[item]}")

# REMOVE ITEM
async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update): return
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /remove item qty")
        return

    item = context.args[0]
    try:
        qty = int(context.args[1])
    except:
        await update.message.reply_text("Quantity must be number")
        return

    stock = load_stock()
    stock[item] = max(0, stock.get(item,0)-qty)
    save_stock(stock)

    remaining = stock[item]
    msg = f"{item} left: {remaining}"

    if remaining == 0:
        msg += "\n⛔ OUT OF STOCK — deactivate Etsy listing!"
    elif remaining == 1:
        msg += "\n⚠ LOW STOCK WARNING (only 1 remaining)"

    await update.message.reply_text(msg)

# SHOW STOCK
async def stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update): return
    data = load_stock()
    if not data:
        await update.message.reply_text("Inventory empty")
        return
    text="\n".join([f"{k}: {v}" for k,v in data.items()])
    await update.message.reply_text(text)

# ---------------- MATERIALS ----------------
MAT_FILE="materials.json"

def load_mat():
    if not os.path.exists(MAT_FILE):
        return {"steel":{}, "wood":{}, "leather":{}}
    return json.load(open(MAT_FILE))

def save_mat(data):
    json.dump(data, open(MAT_FILE,"w"))

async def steel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update): return
    if len(context.args)<3: return
    action,name,qty=context.args[0],context.args[1],int(context.args[2])
    data=load_mat()
    if action=="add":
        data["steel"][name]=data["steel"].get(name,0)+qty
    else:
        data["steel"][name]=max(0,data["steel"].get(name,0)-qty)
    save_mat(data)
    await update.message.reply_text(f"Steel {name}: {data['steel'][name]}")

async def wood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update): return
    if len(context.args)<3: return
    action,name,qty=context.args[0],context.args[1],int(context.args[2])
    data=load_mat()
    if action=="add":
        data["wood"][name]=data["wood"].get(name,0)+qty
    else:
        data["wood"][name]=max(0,data["wood"].get(name,0)-qty)
    save_mat(data)
    await update.message.reply_text(f"Wood {name}: {data['wood'][name]}")

async def leather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update): return
    if len(context.args)<3: return
    action,name,qty=context.args[0],context.args[1],int(context.args[2])
    data=load_mat()
    if action=="add":
        data["leather"][name]=data["leather"].get(name,0)+qty
    else:
        data["leather"][name]=max(0,data["leather"].get(name,0)-qty)
    save_mat(data)
    await update.message.reply_text(f"Leather {name}: {data['leather'][name]}")

async def material(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update): return
    data=load_mat()
    text="STEEL:\n"
    for k,v in data["steel"].items(): text+=f"{k}: {v}\n"
    text+="\nWOOD:\n"
    for k,v in data["wood"].items(): text+=f"{k}: {v}\n"
    text+="\nLEATHER:\n"
    for k,v in data["leather"].items(): text+=f"{k}: {v}\n"
    await update.message.reply_text(text)

# ---------------- ORDERS ----------------
ORDER_FILE="orders.json"

def load_orders():
    if not os.path.exists(ORDER_FILE): return {}
    return json.load(open(ORDER_FILE))

def save_orders(data):
    json.dump(data, open(ORDER_FILE,"w"))

async def order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update): return
    if len(context.args)<2: return
    action,name=context.args[0],context.args[1]
    data=load_orders()

    if action=="add":
        if len(context.args)<3: return
        item=context.args[2]
        data[name]=item
        save_orders(data)
        await update.message.reply_text(f"Order added: {name} -> {item}")
    elif action=="done":
        if name in data:
            del data[name]
            save_orders(data)
            await update.message.reply_text(f"Order completed: {name}")

async def orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update): return
    data=load_orders()
    if not data:
        await update.message.reply_text("No pending orders")
        return
    text="PENDING ORDERS:\n"
    for k,v in data.items(): text+=f"{k} -> {v}\n"
    await update.message.reply_text(text)

# ---------------- START ----------------
app=ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("add",add))
app.add_handler(CommandHandler("remove",remove))
app.add_handler(CommandHandler("stock",stock))
app.add_handler(CommandHandler("steel",steel))
app.add_handler(CommandHandler("wood",wood))
app.add_handler(CommandHandler("leather",leather))
app.add_handler(CommandHandler("material",material))
app.add_handler(CommandHandler("order",order))
app.add_handler(CommandHandler("orders",orders))

app.run_polling()
