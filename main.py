import json, os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

DB_FILE = "gmail.json"
TOKEN = os.getenv("BOT_TOKEN") # nanti isi di hosting

def load_db():
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, "r") as f:
        try:
            return json.load(f)
        except:
            return []

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 STORGMAIL BOT AKTIF!\n\n"
        "/add email:pass - tambah gmail\n"
        "/list - lihat semua\n"
        "/del email - hapus\n"
        "/cek email - cari\n"
        "Contoh: /add test@gmail.com:password123"
    )

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Format: /add email:pass")
        return
    text = " ".join(context.args)
    if ":" not in text:
        await update.message.reply_text("Harus pake : contoh test@gmail.com:pass123")
        return
    email, pwd = text.split(":", 1)
    db = load_db()
    db.append({"email": email.strip(), "pass": pwd.strip()})
    save_db(db)
    await update.message.reply_text(f"✅ Berhasil simpan: {email}")

async def list_gmail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = load_db()
    if not db:
        await update.message.reply_text("Kosong bos")
        return
    msg = f"📦 Total {len(db)} gmail:\n\n"
    for i, d in enumerate(db, 1):
        msg += f"{i}. {d['email']}:{d['pass']}\n"
    # telegram limit 4096
    if len(msg) > 4000:
        msg = msg[:4000] + "\n...kepotong"
    await update.message.reply_text(msg)

async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Format: /del emailnya")
        return
    email = context.args[0]
    db = load_db()
    new_db = [x for x in db if x['email'] != email]
    if len(new_db) == len(db):
        await update.message.reply_text("❌ Gak ketemu email itu")
        return
    save_db(new_db)
    await update.message.reply_text(f"🗑️ Dihapus: {email}")

async def cek(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Format: /cek email")
        return
    q = context.args[0].lower()
    db = load_db()
    found = [x for x in db if q in x['email'].lower()]
    if not found:
        await update.message.reply_text("Gak ketemu")
        return
    msg = "\n".join([f"{x['email']}:{x['pass']}" for x in found])
    await update.message.reply_text(msg)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("list", list_gmail))
    app.add_handler(CommandHandler("del", delete))
    app.add_handler(CommandHandler("cek", cek))
    print("BOT RUNNING...")
    app.run_polling()

if __name__ == "__main__":
    main()
