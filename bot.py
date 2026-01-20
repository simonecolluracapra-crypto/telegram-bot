from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    Filters,
    CallbackContext
)
import matplotlib.pyplot as plt
from collections import defaultdict
import os
import random
import string
import re
from datetime import datetime

# ================= CONFIG =================
TOKEN = "7524793468:AAHIzduLfqX849Y7NUTgjysxbXWV8mcOnD0"
ADMIN_ID = 7727871418
FEEDBACK_CHANNEL_ID = -1003029778967
ADMIN_USERNAME = "@neorich_resell"
BOT_USERNAME = "@NeoRichResellBOT"

PRODUCTS = {
    "25 Fornitori abbigliamento 👕": 15,
    "3 Fornitori ita 🇮🇹": 10,
    "22 Fornitori accessori 🎧": 15,
    "TUTTI I FORNITORI 🔥": 30,
    "Metodo refund Amazon 🛒": 5,
    "Metodo refund Nike 👟": 5,
    "Metodo refund Temu 📦": 5,
    "Metodo refund Glovo/Deliveroo 🍔": 5,
    "Metodo refund Shein 👗": 5,
    "Metodo refund Aliexpress 📦": 5,
    "Metodo refund Zara 👗": 5,
    "Metodo refund Zalando 🛒": 5,
    "TUTTI I METODI REFUND 🔥": 30,
    "Percorso shopify 🛍️": 15,
    "Metodo steam 🎮": 15,
    "Metodo recensioni Vinted ⭐": 10,
}

FILES = {
    "25 Fornitori abbigliamento 👕": "files/fornitori_abbigliamento.pdf",
    "3 Fornitori ita 🇮🇹": "files/fornitori_italia.pdf",
    "22 Fornitori accessori 🎧": "files/fornitori_accessori.pdf",
    "TUTTI I FORNITORI 🔥": "files/tutti_fornitori.pdf",
    "Metodo refund Amazon 🛒": "files/refund_amazon.pdf",
    "Metodo refund Nike 👟": "files/refund_nike.pdf",
    "Metodo refund Temu 📦": "files/refund_temu.pdf",
    "Metodo refund Glovo/Deliveroo 🍔": "files/refund_food.pdf",
    "Metodo refund Shein 👗": "files/refund_shein.pdf",
    "Metodo refund Aliexpress 📦": "files/refund_aliexpress.pdf",
    "Metodo refund Zara 👗": "files/refund_zara.pdf",
    "Metodo refund Zalando 🛒": "files/refund_zalando.pdf",
    "TUTTI I METODI REFUND 🔥": "files/tutti_refund.pdf",
    "Percorso shopify 🛍️": "files/shopify.pdf",
    "Metodo steam 🎮": "files/steam.pdf",
    "Metodo recensioni Vinted ⭐": "files/vinted.pdf",
}

PAYMENTS = {
    "PayPal": (
        "💳 <b>PayPal</b>\n"
        "Invia a:\n"
        "paypal.com/paypalme/SimoneCollura679\n\n"
        "⚠️ <b>Invia come AMICI E FAMILIARI</b>"
    ),
    "Gift Card": f"🎁 Gift Card\nContatta {ADMIN_USERNAME}",
    "Crypto": f"🪙 Crypto\nContatta {ADMIN_USERNAME}",
    "Bonifico": f"🏦 Bonifico\nContatta {ADMIN_USERNAME}",
}

# --------- UTILITY ---------
def genera_codice():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def codice_usato(codice):
    if not os.path.exists("used_codes.txt"):
        return False
    with open("used_codes.txt", "r", encoding="utf-8") as f:
        return codice in f.read()

def segna_codice_usato(codice):
    with open("used_codes.txt", "a", encoding="utf-8") as f:
        f.write(codice + "\n")

def salva_ordine(user, prodotto, prezzo, metodo, codice, stato):
    with open("orders.txt", "a", encoding="utf-8") as f:
        f.write(
            f"{datetime.now()} | "
            f"ID:{user.id} | "
            f"User:@{user.username} | "
            f"Nome:{user.first_name} | "
            f"Prodotto:{prodotto} | "
            f"Prezzo:{prezzo} | "
            f"Metodo:{metodo} | "
            f"Codice:{codice} | "
            f"Stato:{stato}\n"
        )

def aggiorna_stato(codice, nuovo_stato):
    if not os.path.exists("orders.txt"):
        return
    with open("orders.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()
    with open("orders.txt", "w", encoding="utf-8") as f:
        for line in lines:
            if f"Codice:{codice}" in line:
                line = line.replace("Stato:IN ATTESA", f"Stato:{nuovo_stato}")
            f.write(line)

# ----------------- BOT FUNZIONI -----------------
def start(update: Update, context: CallbackContext):
    keyboard = [[InlineKeyboardButton(p, callback_data=f"prod:{p}")] for p in PRODUCTS]
    update.message.reply_text(
        "🛒 <b>Catalogo prodotti</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def button(update: Update, context: CallbackContext):
    q = update.callback_query

    try:
        q.answer()
    except:
        return  # evita crash se il bottone è vecchio

    user = q.from_user
    data = q.data

    if data.startswith("prod:"):
        prodotto = data.split("prod:")[1]
        prezzo = PRODUCTS[prodotto]
        keyboard = [[InlineKeyboardButton(m, callback_data=f"pay:{prodotto}:{m}")] for m in PAYMENTS]
        keyboard.append([InlineKeyboardButton("⬅ Indietro", callback_data="back")])
        q.edit_message_text(
            f"📦 {prodotto}\n💰 €{prezzo}\n\n"
            f"Scegli pagamento\n<i>Per info contatta {ADMIN_USERNAME}</i>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data.startswith("pay:"):
        _, prodotto, metodo = data.split(":")
        prezzo = PRODUCTS[prodotto]
        codice = genera_codice()
        salva_ordine(user, prodotto, prezzo, metodo, codice, "IN ATTESA")
        context.user_data["codice"] = codice
        context.user_data["prodotto"] = prodotto
        context.user_data["attende_codice"] = False
        q.edit_message_text(
            f"{PAYMENTS[metodo]}\n\n💰 Importo: €{prezzo}",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Ho pagato", callback_data="paid")],
                [InlineKeyboardButton("⬅ Indietro", callback_data="back")]
            ])
        )

    elif data == "paid":
        codice = context.user_data.get("codice")
        prodotto = context.user_data.get("prodotto")
        if not codice or not prodotto:
            q.edit_message_text("❌ Errore interno: dati mancanti.")
            return
        context.bot.send_message(
            ADMIN_ID,
            f"🧾 PAGAMENTO SEGNALATO\nUtente: @{user.username}\nID: {user.id}\nProdotto: {prodotto}\nCodice: {codice}"
        )
        context.user_data["attende_codice"] = True
        q.edit_message_text(
            f"✅ Pagamento segnalato.\n"
            f"📩 Contatta {ADMIN_USERNAME} per ricevere il codice.\n"
            "❗ Da qui non puoi tornare indietro",
            parse_mode="HTML"
        )

    elif data == "back":
        keyboard = [[InlineKeyboardButton(p, callback_data=f"prod:{p}")] for p in PRODUCTS]
        q.edit_message_text(
            "🛒 <b>Catalogo prodotti</b>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# ---------- CODICE e ORDINI ----------
# ---------- MESSAGGI TESTO (CODICE + FEEDBACK) ----------
def ricevi_testo(update: Update, context: CallbackContext):
    text = update.message.text.strip()

    # ===== FEEDBACK =====
    if context.user_data.get("attende_feedback"):
        user = update.effective_user
        prodotto = context.user_data.get("feedback_prodotto")
        prezzo = context.user_data.get("feedback_prezzo")

        match = re.match(r"([1-5])\s*\|\s*(.+)", text)
        if not match:
            update.message.reply_text(
                "❌ Formato errato.\n\n"
                "Scrivi così:\n"
                "5 | Prodotto top, super serio 🔥"
            )
            return

        stelle = match.group(1)
        feedback = match.group(2)

        messaggio = (
            f"⭐ FEEDBACK IN ATTESA\n\n"
            f"👤 @{user.username}\n"
            f"📦 {prodotto}\n"
            f"💰 €{prezzo}\n"
            f"⭐ {stelle}/5\n\n"
            f"💬 {feedback}"
        )

        with open("feedback_pending.txt", "a", encoding="utf-8") as f:
            f.write(messaggio + "\n---\n")

        context.bot.send_message(ADMIN_ID, messaggio)

        update.message.reply_text(
            "🙏 Feedback ricevuto! Grazie davvero 💙\n\n"
            f"📸 Per eventuali screenshot scrivi a {ADMIN_USERNAME}"
        )

        context.user_data.clear()
        return

    # ===== CODICE =====
    if not context.user_data.get("attende_codice"):
        return

    codice_inserito = text
    codice_utente = context.user_data.get("codice")
    prodotto = context.user_data.get("prodotto")

    if codice_usato(codice_inserito):
        update.message.reply_text("❌ Codice già usato.")
        return

    if codice_inserito != codice_utente:
        update.message.reply_text("❌ Codice errato. Riprova.")
        return

    context.user_data["attende_codice"] = False

    file_path = FILES.get(prodotto)
    if file_path and os.path.exists(file_path):
        with open(file_path, "rb") as f:
            update.message.reply_document(f, caption="✅ Ordine completato")

    segna_codice_usato(codice_inserito)
    aggiorna_stato(codice_inserito, "COMPLETATO")

    update.message.reply_text(
        "✅ Ordine completato!\n\n"
        "📝 LASCIA UN FEEDBACK\n\n"
        "Scrivi così:\n"
        "5 | Prodotto top 🔥\n\n"
        "⭐ Valutazioni:\n"
        "5 = eccellente\n"
        "4 = molto buono\n"
        "3 = buono\n"
        "2 = migliorabile\n"
        "1 = pessimo\n\n"
        f"📸 Per eventuali screenshot scrivi a {ADMIN_USERNAME}"
    )

    context.user_data["attende_feedback"] = True
    context.user_data["feedback_prodotto"] = prodotto
    context.user_data["feedback_prezzo"] = PRODUCTS[prodotto]

# ---------- APPROVE FEEDBACK ----------
def approve(update: Update, context: CallbackContext):
    if update.message.from_user.id != ADMIN_ID:
        return

    if not os.path.exists("feedback_pending.txt"):
        update.message.reply_text("Nessun feedback.")
        return

    with open("feedback_pending.txt", "r", encoding="utf-8") as f:
        contenuto = f.read()

    if not contenuto.strip():
        update.message.reply_text("Nessun feedback.")
        return

    blocchi = contenuto.split("\n---\n")
    feedback = blocchi[0]

    # 🔹 estrai stelle dal testo
    match = re.search(r"⭐ (\d)/5", feedback)
    stelle = int(match.group(1)) if match else 5

    # 🔹 leggi conteggio precedente
    if os.path.exists("feedback_count.txt"):
        count = int(open("feedback_count.txt").read())
    else:
        count = 65

    # 🔹 leggi stelle precedenti
    sum_stelle = 308

    if os.path.exists("feedback_stars.txt"):
        with open("feedback_stars.txt", "r", encoding="utf-8") as f:
            for line in f:
                try:
                    sum_stelle += int(line.strip())
                except:
                    pass

    # aggiorna
    count += 1
    sum_stelle += stelle
    media = round(sum_stelle / count, 1)

    # salva
    open("feedback_count.txt", "w").write(str(count))
    with open("feedback_stars.txt", "a") as f:
        f.write(str(stelle) + "\n")

    # 🔹 testo per il canale
    feedback_canale = feedback.replace(
        "FEEDBACK IN ATTESA",
        "FEEDBACK COMPLETATO"
    )

    context.bot.send_message(
        FEEDBACK_CHANNEL_ID,
        feedback_canale +
        f"\n\n🤖 {BOT_USERNAME}"
        f"\n📊 Feedback totali: {count}"
        f"\n📈 Media stelle: {media}"
    )

    # rimuove feedback approvato
    open("feedback_pending.txt", "w").write("\n---\n".join(blocchi[1:]))

    update.message.reply_text(
        f"✅ Feedback pubblicato\n📊 Totale: {count} | Media: {media}"
    )

def reject(update: Update, context: CallbackContext):
    if update.message.from_user.id != ADMIN_ID:
        return

    if not os.path.exists("feedback_pending.txt"):
        update.message.reply_text("Nessun feedback in attesa.")
        return

    with open("feedback_pending.txt", "r", encoding="utf-8") as f:
        contenuto = f.read()

    if not contenuto.strip():
        update.message.reply_text("Nessun feedback in attesa.")
        return

    blocchi = contenuto.split("\n---\n")

    # elimina il primo feedback
    open("feedback_pending.txt", "w").write("\n---\n".join(blocchi[1:]))

    update.message.reply_text("❌ Feedback rifiutato ed eliminato.")

def edit_feedback(update: Update, context: CallbackContext):
    if update.message.from_user.id != ADMIN_ID:
        return

    if not context.args:
        update.message.reply_text("❌ Usa: /edit nuovo testo recensione")
        return

    if not os.path.exists("feedback_pending.txt"):
        update.message.reply_text("Nessun feedback.")
        return

    with open("feedback_pending.txt", "r", encoding="utf-8") as f:
        contenuto = f.read()

    if not contenuto.strip():
        update.message.reply_text("Nessun feedback.")
        return

    blocchi = contenuto.split("\n---\n")
    feedback = blocchi[0]

    nuovo_testo = " ".join(context.args)

    feedback_mod = re.sub(
        r"💬 .*",
        f"💬 {nuovo_testo}",
        feedback
    )

    blocchi[0] = feedback_mod

    with open("feedback_pending.txt", "w", encoding="utf-8") as f:
        f.write("\n---\n".join(blocchi))

    update.message.reply_text("✏️ Feedback modificato. Ora puoi usare /approve.")


# ---------- ADMIN ----------

def admin(update: Update, context: CallbackContext):
    if update.message.from_user.id != ADMIN_ID:
        return
    update.message.reply_text(
        "🛠 <b>PANNELLO ADMIN</b>\n\n"
        "📦 <b>ORDINI</b>\n"
        "/orders → ultimi ordini\n"
        "/check CODICE → dettagli ordine\n"
        "/complete CODICE → completa ordine\n\n"
        "📊 <b>STATISTICHE</b>\n"
        "/stats → statistiche generali\n"
        "/stats_mese → statistiche mensili\n\n"
        "📈 <b>GRAFICI</b>\n"
        "/grafico → grafico vendite\n\n"
        "⚙️ <b>SISTEMA</b>\n"
        "/admin → questo pannello",
        parse_mode="HTML"
    )

def orders(update: Update, context: CallbackContext):
    if update.message.from_user.id != ADMIN_ID:
        return
    if not os.path.exists("orders.txt"):
        update.message.reply_text("Nessun ordine.")
        return
    with open("orders.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()[-5:]
    update.message.reply_text("".join(lines))

def check(update: Update, context: CallbackContext):
    if update.message.from_user.id != ADMIN_ID:
        return
    codice = context.args[0]
    with open("orders.txt", "r", encoding="utf-8") as f:
        for line in f:
            if codice in line:
                update.message.reply_text(line)
                return
    update.message.reply_text("Codice non trovato")

def complete(update: Update, context: CallbackContext):
    if update.message.from_user.id != ADMIN_ID:
        return
    codice = context.args[0]
    aggiorna_stato(codice, "COMPLETATO")
    segna_codice_usato(codice)
    update.message.reply_text("✅ Ordine completato manualmente")

def stats(update: Update, context: CallbackContext):
    if update.message.from_user.id != ADMIN_ID:
        return
    if not os.path.exists("orders.txt"):
        update.message.reply_text("Nessuna statistica disponibile.")
        return
    totale_incasso = 0
    tot_ordini = 0
    completati = 0
    attesa = 0
    prodotti = {}
    metodi = {}
    with open("orders.txt", "r", encoding="utf-8") as f:
        for line in f:
            tot_ordini += 1
            if "Stato:COMPLETATO" in line:
                completati += 1
            else:
                attesa += 1
            try:
                prezzo = int(line.split("Prezzo:")[1].split(" |")[0])
                totale_incasso += prezzo
            except:
                pass
            try:
                prod = line.split("Prodotto:")[1].split(" |")[0]
                prodotti[prod] = prodotti.get(prod, 0) + 1
            except:
                pass
            try:
                met = line.split("Metodo:")[1].split(" |")[0]
                metodi[met] = metodi.get(met, 0) + 1
            except:
                pass
    testo = (
        "📊 <b>STATISTICHE VENDITA</b>\n\n"
        f"📦 Ordini totali: {tot_ordini}\n"
        f"✅ Completati: {completati}\n"
        f"⏳ In attesa: {attesa}\n"
        f"💰 Incasso totale: €{totale_incasso}\n\n"
        "🛒 <b>Prodotti più venduti:</b>\n"
    )
    for p, n in prodotti.items():
        testo += f"• {p}: {n}\n"
    testo += "\n💳 <b>Metodi di pagamento:</b>\n"
    for m, n in metodi.items():
        testo += f"• {m}: {n}\n"
    update.message.reply_text(testo, parse_mode="HTML")

def stats_mese(update: Update, context: CallbackContext):
    if update.message.from_user.id != ADMIN_ID:
        return
    mese_corrente = datetime.now().strftime("%Y-%m")
    totale = 0
    ordini = 0
    with open("orders.txt", "r", encoding="utf-8") as f:
        for line in f:
            if mese_corrente in line and "Stato:COMPLETATO" in line:
                ordini += 1
                prezzo = int(line.split("Prezzo:")[1].split(" |")[0])
                totale += prezzo
    update.message.reply_text(
        f"📅 STATISTICHE MESE\n\n💰 Incasso mese: €{totale}\n📦 Ordini completati: {ordini}"
    )

def top(update: Update, context: CallbackContext):
    if update.message.from_user.id != ADMIN_ID:
        return
    prodotti = defaultdict(int)
    with open("orders.txt", "r", encoding="utf-8") as f:
        for line in f:
            try:
                prod = line.split("Prodotto:")[1].split(" |")[0]
                prodotti[prod] += 1
            except:
                pass
    top3 = sorted(prodotti.items(), key=lambda x: x[1], reverse=True)[:3]
    testo = "🏆 <b>TOP 3 PRODOTTI</b>\n"
    for p, n in top3:
        testo += f"• {p}: {n}\n"
    update.message.reply_text(testo, parse_mode="HTML")

def grafico(update: Update, context: CallbackContext):
    if update.message.from_user.id != ADMIN_ID:
        return
    prodotti = defaultdict(int)
    with open("orders.txt", "r", encoding="utf-8") as f:
        for line in f:
            try:
                prod = line.split("Prodotto:")[1].split(" |")[0]
                prodotti[prod] += 1
            except:
                pass
    plt.bar(prodotti.keys(), prodotti.values())
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig("grafico.png")
    plt.close()
    with open("grafico.png", "rb") as f:
        update.message.reply_document(f, filename="grafico.png")

# ---- MAIN ----
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("admin", admin))
    dp.add_handler(CommandHandler("orders", orders))
    dp.add_handler(CommandHandler("check", check))
    dp.add_handler(CommandHandler("complete", complete))
    dp.add_handler(CommandHandler("stats", stats))
    dp.add_handler(CommandHandler("stats_mese", stats_mese))
    dp.add_handler(CommandHandler("top", top))
    dp.add_handler(CommandHandler("grafico", grafico))
    dp.add_handler(CommandHandler("edit", edit_feedback))
    dp.add_handler(CommandHandler("reject", reject))
    dp.add_handler(CommandHandler("approve", approve))

    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, ricevi_testo))


    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
