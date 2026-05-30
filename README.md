# 🔐 Bot CCAR — Cifrado con Hash en Telegram

Bot de Telegram que implementa el algoritmo de hash **CCAR** (Cazorla, Chambia, Avilés, Rivero), basado en permutación dinámica, suma modular y mezcla XOR con buffer. La clave del sistema es interna y nunca se expone al usuario.

---

## Estructura del proyecto

```
bot_cifrador/
├── bot.py          # Lógica del bot de Telegram
├── cifrador.py     # Algoritmo CCAR (hash y verificación)
├── requirements.txt
└── README.md
```

---

## Requisitos

- Python 3.11 o superior
- Cuenta en Telegram
- Token de bot (ver Configuración)

---

## Instalación

**1. Clonar o descargar el proyecto**

```bash
# Descargar los archivos en una carpeta, por ejemplo:
mkdir bot_cifrador
cd bot_cifrador
```

**2. Instalar dependencias**

```bash
pip install python-telegram-bot==21.5
```

---

## Configuración

**1. Crear el bot en Telegram**

- Abre Telegram y busca **@BotFather**
- Escribe `/newbot`
- Elige un nombre (ej. `Cifrador CCAR`)
- Elige un username (ej. `cifrador_ccar_bot`)
- BotFather te dará un token como: `7123456789:AAFxyz...`

**2. Pegar el token en `bot.py`**

Abre `bot.py` y reemplaza en la línea 18:

```python
TOKEN = "TU_TOKEN_AQUI"
```

**3. (Opcional) Cambiar la seed del sistema**

La seed es la clave interna del algoritmo. Puedes cambiarla en la línea 21 de `bot.py`:

```python
_SEED = "TU_FRASE_SECRETA_AQUI"
```

> ⚠️ Si cambias la seed después de haber generado hashes, los hashes anteriores ya no se podrán verificar.

---

## Uso

**Iniciar el bot**

```bash
python bot.py
```

Debería aparecer:
```
🤖 Bot CCAR iniciado. Esperando mensajes... (Ctrl+C para detener)
```

Para detenerlo: `Ctrl + C`

---

## Comandos del bot

| Comando | Descripción | Ejemplo |
|---|---|---|
| `/start` | Bienvenida e introducción | `/start` |
| `/ayuda` | Instrucciones paso a paso | `/ayuda` |
| `/hash <texto>` | Genera el hash CCAR del texto | `/hash MiContraseña123` |
| `/verificar <texto> <salt> <hash>` | Verifica si el texto coincide con un hash guardado | `/verificar MiContraseña123 a3f8b2... 9d4e7f...` |

### Flujo de uso típico

```
1. Usuario: /hash MiContraseña123

   Bot responde:
   ✅ Hash CCAR generado
   🔑 Salt: a3f8b2c1d5e9f042
   🔒 Hash: 9d4e7f2a1b3c...

2. (El usuario guarda el salt y el hash)

3. Usuario: /verificar MiContraseña123 a3f8b2c1d5e9f042 9d4e7f2a1b3c...

   Bot responde:
   ✅ Verificación exitosa
```

> Nota: el mismo texto genera un hash diferente cada vez por el salt aleatorio. Para verificar siempre se necesitan los tres valores: texto, salt y hash.

---

## Cómo funciona el algoritmo CCAR

El algoritmo aplica **50 rondas** de transformación sobre el texto de entrada. En cada ronda:

1. **Salt aleatorio** — se genera un salt de 8 bytes al momento de hashear.
2. **Clave dinámica** — en cada ronda, la clave se recalcula combinando la seed del sistema, el número de ronda y el estado actual de los datos.
3. **Cifrado por bloques** — los datos se dividen en bloques de tamaño dinámico, se aplica suma modular y luego permutación.
4. **Mezcla con buffer** — operación XOR con retroalimentación que hace que cada byte dependa del historial anterior.
5. **Salida hexadecimal** — los bytes resultantes se convierten a string hexadecimal.

El hash es **unidireccional**: no se puede recuperar el texto original a partir del hash.

---

## Mantener el bot activo

**Opción A — Uso inmediato (PC encendida)**

Simplemente deja la terminal abierta con `python bot.py` corriendo.

**Opción B — 24/7 gratis con Railway**

1. Sube los archivos a un repositorio en [GitHub](https://github.com)
2. Entra a [railway.app](https://railway.app) → New Project → Deploy from GitHub
3. Agrega la variable de entorno: `TOKEN = tu_token`
4. En `bot.py` cambia la línea del token por:
   ```python
   import os
   TOKEN = os.environ["TOKEN"]
   ```
5. Haz deploy — el bot correrá de forma permanente y gratuita.

---

## Autores

**Cazorla · Chambia · Avilés · Rivero**
