"""
Algoritmo de cifrado simétrico personalizado
Basado en: permutación dinámica + suma modular + mezcla XOR
"""

MOD    = 256
RONDAS = 10

# ══════════════════════════════════════════════════
#  UTILIDADES
# ══════════════════════════════════════════════════

def texto_a_bytes(texto: str) -> list:
    return list(texto.encode("utf-8"))

def bytes_a_texto(lista: list) -> str:
    return bytes(lista).decode("utf-8", errors="ignore")

def bytes_a_hex(lista: list) -> str:
    return "".join(format(b, "02x") for b in lista)

# ══════════════════════════════════════════════════
#  PERMUTACIÓN DINÁMICA
# ══════════════════════════════════════════════════

def generar_perm(clave_bytes: list, tam: int, ronda: int) -> list:
    subclave = clave_bytes.copy()
    while len(subclave) < tam:
        subclave += clave_bytes
    subclave = subclave[:tam]

    pares = list(enumerate(subclave))
    pares.sort(key=lambda x: x[1])
    perm = [i for i, _ in pares]

    k = ronda % tam
    return perm[k:] + perm[:k]

def inversa_perm(perm: list) -> list:
    """Calcula la permutación inversa."""
    inv = [0] * len(perm)
    for i, p in enumerate(perm):
        inv[p] = i
    return inv

def aplicar_perm(bloque: list, perm: list) -> list:
    return [bloque[i] for i in perm]

# ══════════════════════════════════════════════════
#  BUFFER DETERMINISTA POR RONDA
#  (derivado solo de clave + nro de ronda, sin estado mutable)
#  Esto permite revertirlo exactamente igual en el descifrado
# ══════════════════════════════════════════════════

def generar_buffer(clave_bytes: list, ronda: int, size: int = 512) -> list:
    semilla = clave_bytes + [ronda % 256, (ronda * 7 + 13) % 256]
    return [(semilla[i % len(semilla)] ^ i ^ ronda) % 256 for i in range(size)]

def mezclar_xor(data: list, buffer: list) -> list:
    """XOR con el buffer. Es su propia inversa: aplicar 2 veces = datos originales."""
    return [data[i] ^ buffer[i % len(buffer)] for i in range(len(data))]

# ══════════════════════════════════════════════════
#  RONDA DE CIFRADO
# ══════════════════════════════════════════════════

def ronda_cifrado(data_bytes: list, clave_bytes: list, ronda: int) -> list:
    resultado = []
    i      = 0
    k_idx  = 0

    while i < len(data_bytes):
        tam    = (clave_bytes[k_idx % len(clave_bytes)] % 5) + 2
        bloque = list(data_bytes[i : i + tam])

        # Padding si el último bloque es corto
        if len(bloque) < tam:
            bloque += [0] * (tam - len(bloque))

        k = clave_bytes[k_idx % len(clave_bytes)]

        # 1. Suma modular
        bloque = [(x + k + ronda) % MOD for x in bloque]

        # 2. Permutación dinámica
        perm   = generar_perm(clave_bytes, len(bloque), ronda)
        bloque = aplicar_perm(bloque, perm)

        resultado.extend(bloque)
        i     += tam
        k_idx += 1

    return resultado

# ══════════════════════════════════════════════════
#  RONDA DE DESCIFRADO  (operaciones en orden inverso)
# ══════════════════════════════════════════════════

def ronda_descifrado(data_bytes: list, clave_bytes: list, ronda: int) -> list:
    resultado = []
    i     = 0
    k_idx = 0

    while i < len(data_bytes):
        tam    = (clave_bytes[k_idx % len(clave_bytes)] % 5) + 2
        bloque = list(data_bytes[i : i + tam])

        if len(bloque) < tam:
            bloque += [0] * (tam - len(bloque))

        k = clave_bytes[k_idx % len(clave_bytes)]

        # Inverso de ronda_cifrado: primero despermutar, luego restar
        perm   = generar_perm(clave_bytes, len(bloque), ronda)
        inv    = inversa_perm(perm)
        bloque = aplicar_perm(bloque, inv)

        bloque = [(x - k - ronda) % MOD for x in bloque]

        resultado.extend(bloque)
        i     += tam
        k_idx += 1

    return resultado

# ══════════════════════════════════════════════════
#  CIFRADO COMPLETO
# ══════════════════════════════════════════════════

def cifrar(mensaje: str, clave: str) -> str:
    """
    Cifra un mensaje con la clave dada.
    Retorna el texto cifrado en hexadecimal.
    """
    data = texto_a_bytes(mensaje)

    # Guardamos la longitud original en 4 bytes (big-endian)
    # para poder recortarla exactamente al descifrar
    length = len(data)
    data = list(length.to_bytes(4, "big")) + data

    for ronda in range(RONDAS):
        clave_r = texto_a_bytes(clave + str(ronda))
        data    = ronda_cifrado(data, clave_r, ronda)
        buf     = generar_buffer(clave_r, ronda)
        data    = mezclar_xor(data, buf)

    return bytes_a_hex(data)


def descifrar(hex_texto: str, clave: str):
    """
    Descifra un texto hexadecimal con la clave dada.
    Retorna el mensaje original (str), o None si falla.
    """
    try:
        data = list(bytes.fromhex(hex_texto.strip()))
    except ValueError:
        return None

    # Recorremos las rondas en orden INVERSO
    for ronda in range(RONDAS - 1, -1, -1):
        clave_r = texto_a_bytes(clave + str(ronda))
        buf     = generar_buffer(clave_r, ronda)
        data    = mezclar_xor(data, buf)        # XOR es su propia inversa
        data    = ronda_descifrado(data, clave_r, ronda)

    if len(data) < 4:
        return None

    # Recuperamos la longitud original
    length = int.from_bytes(bytes(data[:4]), "big")

    if length < 0 or length > len(data) - 4:
        return None  # Clave incorrecta → longitud corrupta

    return bytes_a_texto(data[4 : 4 + length])
