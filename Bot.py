from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import json, os

TOKEN = os.getenv("8656525286")
OWNER_ID = 7153152247   # your telegram numeric ID

STOCK_FILE = "stock.json"
QUEUE_FILE = "queue.json"


# ----------------- FILE SYSTEM -----------------

def load_stock():
    if not os.path.exists(STOCK_FILE):
        return {}
    with open(STOCK_FILE, "r") as f:
        return json.load(f)

def save_stock(data):
    with open(STOCK_FILE, "w") as f:
        json.dump(data, f)


def load_queue():
    if not os.path.exists(QUEUE_FILE):
        return {}
    with open(QUEUE_FILE, "r") as f:
        return json.load(f)

def save_queue(data):
    with open(QUEUE_FILE, "w") as f:
        json.dump(data, f)


def is_owner(update):
    return update.effective_user.id == OWNER_ID


# ----------------- START -----------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update): return
    await update.message.reply_text(
"""Workshop Inventory Bot Ready

Commands:

/add item qty
/remove item qty
/stock
/order add name item
/order done name item
/pending"""
    )


# ----------------- ADD STOCK -----------------

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update): return
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /add item quantity")
        return

    item = context.args[0].lower()
    qty = int(context.args[1])

    stock = load_stock()
    stock[item] = stock.get(item, 0) + qty
    save_stock(stock)

    # check pending orders
    queue = load_queue()

    if item in queue and len(queue[item]) > 0:
        ready = min(qty, len(queue[item]))
        customers = queue[item][:ready]

        msg = f"{qty} {item} added.\n\nDeliver to:\n"
        for c in customers:
            msg += f"- {c}\n"

        await update.message.reply_text(msg)
    else:
        await update.message.reply_text(f"{item} added. Total: {stock[item]}")


# ----------------- REMOVE (SALE / SHIP) -----------------

async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update): return
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /remove item quantity")
        return

    item = context.args[0].lower()
    qty = int(context.args[1])

    stock = load_stock()
    stock[item] = stock.get(item, 0) - qty
    save_stock(stock)

    remaining = stock[item]

    msg = f"{item} left: {remaining}"

    if remaining <= 0:
        msg += "\n⚠ OUT OF STOCK — deactivate Etsy listing!"

    await update.message.reply_text(msg)


# ----------------- STOCK VIEW -----------------

async def stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update): return

    stock = load_stock()
    if not stock:
        await update.message.reply_text("Inventory empty")
        return

    text = "CURRENT STOCK:\n"
    for k, v in stock.items():
        text += f"{k}: {v}\n"

    await update.message.reply_text(text)


# ----------------- ORDER QUEUE -----------------

async def order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update): return
    if len(context.args) < 3:
        await update.message.reply_text("Usage: /order add/done name item")
        return

    action = context.args[0]
    name = context.args[1]
    item = context.args[2].lower()

    queue = load_queue()

    if item not in queue:
        queue[item] = []

    if action == "add":
        queue[item].append(name)
        save_queue(queue)
        await update.message.reply_text(f"Order saved: {name} → {item}")

    elif action == "done":
        if name in queue[item]:
            queue[item].remove(name)
            save_queue(queue)
            await update.message.reply_text(f"Completed: {name}")
        else:
            await update.message.reply_text("Order not found")


# ----------------- PENDING LIST -----------------

async def pending(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update): return

    queue = load_queue()
    if not queue:
        await update.message.reply_text("No pending orders")
        return

    text = "PENDING ORDERS:\n"

    for item, customers in queue.items():
        if customers:
            text += f"\n{item}:\n"
            for i, c in enumerate(customers, 1):
                text += f"{i}) {c}\n"

    await update.message.reply_text(text)


# ----------------- MAIN -----------------

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("add", add))
app.add_handler(CommandHandler("remove", remove))
app.add_handler(CommandHandler("stock", stock))
app.add_handler(CommandHandler("order", order))
app.add_handler(CommandHandler("pending", pending))

print("BOT RUNNING...")
app.run_polling()
