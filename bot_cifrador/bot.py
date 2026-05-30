"""
Bot de Telegram — Cifrador/Descifrador
Requiere: pip install python-telegram-bot

Comandos:
  /start         — bienvenida
  /ayuda         — instrucciones
  /cifrar        — cifra un mensaje
  /descifrar     — descifra un hexadecimal
"""

import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from cifrador import cifrar, descifrar

# ── CONFIGURACIÓN ─────────────────────────────────────────────────────────────
TOKEN = "PEGA_AQUI_TU_TOKEN"   # ← reemplazar con el token de @BotFather

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)

MAX_MENSAJE = 800   # Límite de chars para el mensaje a cifrar


# ── COMANDOS ──────────────────────────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = (
        "🔐 *Bot de Cifrado*\n\n"
        "Puedo cifrar y descifrar mensajes usando un algoritmo "
        "de permutación dinámica + suma modular.\n\n"
        "📌 *Comandos:*\n"
        "• `/cifrar CLAVE tu mensaje aquí`\n"
        "• `/descifrar CLAVE texto\\_en\\_hex`\n"
        "• `/ayuda` — ver ejemplos\n\n"
        "_La clave puede ser cualquier palabra o frase._"
    )
    await update.message.reply_text(texto, parse_mode="Markdown")


async def cmd_ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = (
        "📖 *Cómo usar el bot*\n\n"
        "*🔒 Cifrar un mensaje:*\n"
        "`/cifrar miClave Hola mundo secreto`\n\n"
        "*🔓 Descifrar el resultado:*\n"
        "`/descifrar miClave 0a1b2c3d...`\n\n"
        "⚠️ *Importante:*\n"
        "— La clave debe ser *exactamente igual* para cifrar y descifrar.\n"
        "— El resultado del cifrado es un texto hexadecimal.\n"
        "— Máximo *800 caracteres* por mensaje.\n\n"
        "*Ejemplo completo:*\n"
        "`/cifrar clave123 Texto de prueba`\n"
        "→ El bot responde con el hex cifrado\n"
        "`/descifrar clave123 <hex que devolvió>`\n"
        "→ El bot devuelve `Texto de prueba`"
    )
    await update.message.reply_text(texto, parse_mode="Markdown")


async def cmd_cifrar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args

    if len(args) < 2:
        await update.message.reply_text(
            "❌ *Faltan argumentos.*\n\n"
            "Uso: `/cifrar CLAVE mensaje`\n"
            "Ejemplo: `/cifrar miClave Hola mundo`",
            parse_mode="Markdown",
        )
        return

    clave   = args[0]
    mensaje = " ".join(args[1:])

    if len(mensaje) > MAX_MENSAJE:
        await update.message.reply_text(
            f"⚠️ El mensaje es demasiado largo. Máximo {MAX_MENSAJE} caracteres."
        )
        return

    try:
        resultado = cifrar(mensaje, clave)
        await update.message.reply_text(
            f"🔒 *Mensaje cifrado:*\n\n`{resultado}`\n\n"
            f"_Longitud original: {len(mensaje)} chars → {len(resultado)} hex chars_",
            parse_mode="Markdown",
        )
    except Exception as e:
        logging.error(f"Error al cifrar: {e}")
        await update.message.reply_text(f"⚠️ Error inesperado al cifrar: {e}")


async def cmd_descifrar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args

    if len(args) < 2:
        await update.message.reply_text(
            "❌ *Faltan argumentos.*\n\n"
            "Uso: `/descifrar CLAVE hexadecimal`\n"
            "Ejemplo: `/descifrar miClave 1a2b3c...`",
            parse_mode="Markdown",
        )
        return

    clave     = args[0]
    hex_texto = args[1]

    # Validación rápida
    if not all(c in "0123456789abcdefABCDEF" for c in hex_texto):
        await update.message.reply_text(
            "❌ El texto no parece ser hexadecimal válido.\n"
            "Asegurate de copiar el resultado completo del cifrado."
        )
        return

    try:
        resultado = descifrar(hex_texto, clave)

        if resultado is None:
            await update.message.reply_text(
                "❌ *No se pudo descifrar.*\n\n"
                "Verificá:\n"
                "• Que copiaste el hex *completo* sin espacios\n"
                "• Que la clave sea *exactamente igual* a la usada para cifrar",
                parse_mode="Markdown",
            )
        else:
            await update.message.reply_text(
                f"🔓 *Mensaje descifrado:*\n\n`{resultado}`",
                parse_mode="Markdown",
            )
    except Exception as e:
        logging.error(f"Error al descifrar: {e}")
        await update.message.reply_text(f"⚠️ Error inesperado al descifrar: {e}")


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    if TOKEN == "PEGA_AQUI_TU_TOKEN":
        print("❌  ERROR: Reemplazá TOKEN con el token real de @BotFather en bot.py")
        return

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start",     cmd_start))
    app.add_handler(CommandHandler("ayuda",     cmd_ayuda))
    app.add_handler(CommandHandler("cifrar",    cmd_cifrar))
    app.add_handler(CommandHandler("descifrar", cmd_descifrar))

    print("🤖 Bot iniciado. Esperando mensajes... (Ctrl+C para detener)")
    app.run_polling(poll_interval=1)


if __name__ == "__main__":
    main()
