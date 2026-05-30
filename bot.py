# -*- coding: utf-8 -*-
"""
Bot de Telegram — Cifrado CCAR
La clave del sistema es interna. El usuario solo provee su texto.

Comandos:
  /start      — bienvenida
  /ayuda      — instrucciones
  /hash       — genera hash CCAR de un texto
  /verificar  — verifica si un texto coincide con un hash guardado
  /irvin      — 👀
  /pibble     — 🐶
"""

import asyncio
import logging
import random
import string
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from cifrador import ccar_hash, ccar_verificar

# ── CONFIGURACIÓN ─────────────────────────────────────────────────────────────
TOKEN = "8575945227:AAHkoghACUUqnkh7DBB8h_vqHN3OMVpRhNk"

# Seed del sistema — nunca se muestra al usuario
_SEED = "CCAR_SISTEMA_2024_CazorlaChambiaAvilesRivero"

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)

MAX_TEXTO = 800

# ── CHISTES ───────────────────────────────────────────────────────────────────
CHISTES = [
    "¿Por qué los pájaros vuelan hacia el sur en invierno? ¡Porque caminando tardarían demasiado!",
    "¿Qué le dijo el semáforo al auto? ¡No me mires, me estoy cambiando!",
    "¿Por qué el libro de matemáticas estaba triste? Porque tenía demasiados problemas.",
    "¿Qué hace una abeja en el gimnasio? ¡Zum-ba!",
    "¿Por qué el espantapájaros ganó un premio? Porque era sobresaliente en su campo.",
    "¿Cómo se llama el campeón de buceo de Japón? Tokofondo.",
    "¿Cuál es el colmo de un electricista? Que su hijo sea un conductor.",
    "¿Qué le dijo el 0 al 8? ¡Bonito cinturón!",
    "¿Por qué la escoba está contenta? Porque se enteró de que va a barrer.",
    "¿Cómo se despiden los químicos? Ácido un placer.",
    "¿Qué hace una vaca con un mapa? ¡Encuentra el pasto más cercano!",
    "¿Por qué el sol no fue a la universidad? Porque ya tenía millones de grados.",
    "¿Qué le dijo el gancho al saco? ¡Estás en el gancho!",
    "¿Cuál es el animal más antiguo? El caballo, porque ya está en todos los cuadros.",
    "¿Qué le dijo el mar a la playa? Nada, solo hizo olas.",
    "¿Por qué el café fue al psicólogo? Porque tenía muchos filtros.",
    "¿Cómo llamas a un perro sin patas? No importa, igual no va a venir.",
    "¿Qué le dijo la impresora al papel? Eres mi tipo.",
    "¿Cuál es el músico favorito de los peces? Nemo Clapton.",
    "¿Por qué el fantasma no mintió? Porque era un espíritu transparente.",
    "¿Qué hace un pez cuando se aburre? Nada.",
    "¿Por qué la luna no come? Porque ya está llena.",
    "¿Qué le dijo el techo a la pared? Te veo en la esquina.",
    "¿Por qué el estudiante llevó escalera a la escuela? Porque era secundaria.",
    "¿Cómo se llama el jefe de los dentistas? El muela de la empresa.",
    "¿Qué hace un cocodrilo estudiando medicina? Un doc-toro.",
    "¿Por qué los esqueletos no pelean entre sí? Porque no tienen agallas.",
    "¿Cuál es el cuento más corto? Había una vez... fin.",
    "¿Qué le dijo el semáforo verde al rojo? Espérate.",
    "¿Por qué el tomate fue al médico? Porque no ketchup con nadie.",
    "¿Cómo se llama el cinturón hecho de relojes? Una pérdida de tiempo.",
    "¿Qué le dijo el diente al dentista? ¡No me taladres la paciencia!",
    "¿Por qué el computador fue al médico? Porque tenía un virus.",
    "¿Cómo llamas a un dinosaurio con buena educación? Un cortesaurio.",
    "¿Qué hace la mantequilla cuando está nerviosa? Se derrite.",
    "¿Por qué el número 6 le tiene miedo al 7? Porque 7 se comió al 9.",
    "¿Cuál es el colmo de un jardinero? Que su mujer le ponga los cuernos.",
    "¿Qué le dijo un papel a otro? Oye, somos pliegos.",
    "¿Por qué las bicicletas no pueden pararse solas? Porque están dos-cansadas.",
    "¿Cómo se llama el campeón de natación? Salvador.",
    "¿Qué le dice una pared a la otra? Yo no me meto en tus esquinas.",
    "¿Por qué el maestro llevó anteojos a la escuela? Porque tenía muchos alumnos.",
    "¿Cuál es el colmo de un fumador? Que sus hijos salgan humo.",
    "¿Qué hace un pájaro con internet? Busca en el Googol.",
    "¿Por qué el café nunca gana en el casino? Porque siempre está molido.",
    "¿Qué le dijo el río al mar? ¿Cómo mareas?",
    "¿Por qué la galleta fue al doctor? Porque se sentía desmoronada.",
    "¿Cómo llamas a un boomerang que no vuelve? Un palo.",
    "¿Qué hace un elefante con la computadora? Aplasta las teclas.",
    "¿Por qué la llave estaba cansada? Porque había tenido un día muy duro.",
    "¿Qué le dijo el frío al calor? No te me acerques, me das calor.",
    "¿Por qué el caracol viajaba en taxi? Porque quería ir más rápido de todas formas.",
    "¿Cuál es el colmo de un pintor? Que su hijo salga manchado.",
    "¿Qué hace una araña en la computadora? Una página web.",
    "¿Por qué la naranja fue al circo? Para hacer jugo malabares.",
    "¿Cómo llamas a un oso sin dientes? Un oso goloso.",
    "¿Qué le dijo el pastel a la vela? ¡Me tienes hasta las mechas!",
    "¿Por qué el piano fue al dentista? Porque tenía las teclas picadas.",
    "¿Qué hace un gato en el computador? Navegar en el inter-net.",
    "¿Por qué el estadio fue al psicólogo? Porque tenía muchas gradas.",
    "¿Cómo se llama el perro de un mago? Labracadabrador.",
    "¿Qué le dice una iguana a su hermana gemela? Somos iguanas.",
    "¿Por qué el libro de historia estaba asustado? Porque tenía muchas fechas.",
    "¿Qué hace un pez payaso? Nada gracioso.",
    "¿Por qué el helado nunca está solo? Porque siempre tiene su cucurucho.",
    "¿Cuál es el colmo de un carpintero? Que su hijo sea un clavo.",
    "¿Qué le dijo la montaña al volcán? Tú sí que eres el más caliente.",
    "¿Por qué los lápices van a la escuela? Para ser más afilados.",
    "¿Cómo llamas a un chiste sin gracia? Este chiste.",
    "¿Qué hace un pez eléctrico en la bañera? Chapuzón con luz.",
    "¿Por qué el loro fue al médico? Porque estaba un poco périco.",
    "¿Qué le dijo el sombrero a la cabeza? Tú arriba, yo te cubro.",
    "¿Por qué el tomate se puso rojo? Porque vio la ensalada sin vestir.",
    "¿Cómo se llama el detective más dulce? Sherlock Flan.",
    "¿Qué hace la luna cuando tiene hambre? Le da una mordida al sol.",
    "¿Por qué el pianista fue a la cárcel? Por hacer escalas.",
    "¿Cuál es el colmo de un fotógrafo? Que su mujer no salga en la foto.",
    "¿Qué le dijo el ojo izquierdo al derecho? Entre nosotros hay algo.",
    "¿Por qué el ciempiés llegó tarde a trabajar? Porque tardó mucho en ponerse los zapatos.",
    "¿Cómo se despiden los hipsters? Hasta luego... pero ya lo escuché antes.",
    "¿Qué hace un gusano en el maíz? El gusanillo de la curiosidad.",
    "¿Por qué la escoba está soltera? Porque espanta a todos.",
    "¿Cómo llamas a un pez que no tiene ojos? Un pz.",
    "¿Qué le dijo el globo al alfiler? ¡Punzante el encuentro!",
    "¿Por qué el astronauta no puede usar internet? Porque pierde la conexión en el espacio.",
    "¿Cuál es el animal que más sabe de informática? El ratón.",
    "¿Qué hace un caracol en una moto? ¡Va despacio de todas formas!",
    "¿Por qué el banco fue al psicólogo? Porque tenía demasiado interés.",
    "¿Cómo llamas a un camello sin joroba? Camilo.",
    "¿Qué le dice el agua al fuego? ¡Que te apago!",
    "¿Por qué el cangrejo nunca comparte? Porque es un poco tacaño.",
    "¿Cuál es el colmo de un electricista? Que la corriente le lleve al trabajo.",
    "¿Qué hace una abeja cuando llueve? Se moja, ¡no tiene paraguas!",
    "¿Por qué el queso fue a la discoteca? Para derretirse en la pista.",
    "¿Cómo llamas a un edificio de 100 pisos? ¡Mucho piso!",
    "¿Qué le dijo el zapato al pie? ¡Me tienes harto de llevar tu peso!",
    "¿Por qué el músico llevó paraguas al concierto? Porque predijeron rock.",
    "¿Qué hace un reloj en el espacio? ¡Cuenta el tiempo interestelar!",
]

# ── COMANDOS ──────────────────────────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = (
        "🔐 *Bot CCAR — Cifrado con Hash*\n\n"
        "Este bot usa el algoritmo CCAR para generar huellas "
        "únicas de cualquier texto\\. La clave del sistema es interna "
        "y nunca se comparte\\.\n\n"
        "📌 *Comandos:*\n"
        "• `/hash <texto>` — genera el hash CCAR de tu texto\n"
        "• `/verificar <texto> <salt> <hash>` — comprueba si coincide\n"
        "• `/ayuda` — ver ejemplos paso a paso"
    )
    await update.message.reply_text(texto, parse_mode="MarkdownV2")


async def cmd_ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = (
        "📖 *Cómo usar el bot CCAR*\n\n"
        "*Paso 1 — Generar hash de un texto:*\n"
        "`/hash MiContraseñaSegura`\n"
        "→ El bot responde con el *hash* y el *salt*\n"
        "→ Guarda ambos, los necesitarás para verificar\n\n"
        "*Paso 2 — Verificar más tarde:*\n"
        "`/verificar MiContraseñaSegura <salt> <hash>`\n"
        "→ El bot te dice si coincide ✅ o no ❌\n\n"
        "⚠️ *Importante:*\n"
        "— El hash es *unidireccional*: no se puede revertir\n"
        "— Cada vez que uses `/hash` con el mismo texto, "
        "el hash será *diferente* por el salt aleatorio\n"
        "— Para verificar siempre necesitas los tres: texto, salt y hash"
    )
    await update.message.reply_text(texto, parse_mode="Markdown")


async def cmd_hash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args

    if not args:
        await update.message.reply_text(
            "❌ *Falta el texto.*\n\n"
            "Uso: `/hash tu texto aqui`\n"
            "Ejemplo: `/hash MiContraseña123`",
            parse_mode="Markdown",
        )
        return

    texto = " ".join(args)

    if len(texto) > MAX_TEXTO:
        await update.message.reply_text(
            f"⚠️ El texto es demasiado largo. Máximo {MAX_TEXTO} caracteres."
        )
        return

    try:
        hash_val, salt = ccar_hash(texto, _SEED)
        respuesta = (
            f"✅ *Hash CCAR generado*\n\n"
            f"🔑 *Salt:*\n`{salt}`\n\n"
            f"🔒 *Hash:*\n`{hash_val}`\n\n"
            f"_Guarda el salt y el hash\\. "
            f"Los necesitas para verificar más tarde\\._"
        )
        await update.message.reply_text(respuesta, parse_mode="MarkdownV2")
    except Exception as e:
        logging.error(f"Error en /hash: {e}")
        await update.message.reply_text(f"⚠️ Error inesperado: {e}")


async def cmd_verificar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args

    # Necesita mínimo 3 args: texto(s), salt, hash
    if len(args) < 3:
        await update.message.reply_text(
            "❌ *Faltan argumentos.*\n\n"
            "Uso: `/verificar <texto> <salt> <hash>`\n\n"
            "Si tu texto tiene espacios, pon el salt y hash al final:\n"
            "`/verificar mi texto con espacios <salt> <hash>`",
            parse_mode="Markdown",
        )
        return

    # El hash es el último arg, el salt es el penúltimo, el texto es todo lo demás
    hash_dado = args[-1]
    salt_dado = args[-2]
    texto     = " ".join(args[:-2])

    # Validar que salt y hash parezcan hex
    def es_hex(s):
        return all(c in "0123456789abcdefABCDEF" for c in s)

    if not es_hex(salt_dado) or not es_hex(hash_dado):
        await update.message.reply_text(
            "❌ El salt o el hash no tienen formato válido.\n"
            "Asegúrate de copiar exactamente los valores que devolvió el bot."
        )
        return

    try:
        resultado = ccar_verificar(texto, _SEED, salt_dado, hash_dado)

        if resultado:
            await update.message.reply_text(
                "✅ *Verificación exitosa*\n\n"
                "El texto coincide con el hash guardado.",
                parse_mode="Markdown",
            )
        else:
            await update.message.reply_text(
                "❌ *Verificación fallida*\n\n"
                "El texto *no* coincide con el hash guardado.\n\n"
                "Verifica que:\n"
                "• El texto sea exactamente igual al original\n"
                "• El salt y el hash sean los correctos",
                parse_mode="Markdown",
            )
    except Exception as e:
        logging.error(f"Error en /verificar: {e}")
        await update.message.reply_text(f"⚠️ Error inesperado: {e}")


async def cmd_irvin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chiste = random.choice(CHISTES)
    await update.message.reply_text(
        f"{chiste}\n\n_...jaja_",
        parse_mode="Markdown",
    )


async def cmd_pibble(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_animation(
        animation="https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExOTl6MGl6dGlicWhqMTdkazZlcDlmNGp3amRqMjdsM2N1OGx6ZXk0MSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/tsVy43fVemIsfe4o6t/giphy.gif"
    )


# ── MAIN ──────────────────────────────────────────────────────────────────────

async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start",     cmd_start))
    app.add_handler(CommandHandler("ayuda",     cmd_ayuda))
    app.add_handler(CommandHandler("hash",      cmd_hash))
    app.add_handler(CommandHandler("verificar", cmd_verificar))
    app.add_handler(CommandHandler("irvin",     cmd_irvin))
    app.add_handler(CommandHandler("pibble",    cmd_pibble))

    print("🤖 Bot CCAR iniciado. Esperando mensajes... (Ctrl+C para detener)")

    async with app:
        await app.start()
        await app.updater.start_polling(poll_interval=1)
        await asyncio.Event().wait()
        await app.updater.stop()
        await app.stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⛔ Bot detenido.")