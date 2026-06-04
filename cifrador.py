# -*- coding: utf-8 -*-
"""
Algoritmo CCAR — Cifrado simétrico + Hash con salt
Cazorla, Chambi, Avilés, Rivero
"""

import os

MOD = 256

# ── UTILIDADES ────────────────────────────────────────────────────────────────

def texto_a_bytes(texto):
    return list(texto.encode("utf-8"))

def bytes_a_texto(lista):
    return bytes(lista).decode("utf-8", errors="ignore")

def bytes_a_hex(lista):
    return ''.join(format(b, '02x') for b in lista)

def hex_a_bytes(hexstr):
    return list(bytes.fromhex(hexstr))

# ── PERMUTACIÓN DINÁMICA ──────────────────────────────────────────────────────

def generar_perm(clave_bytes, tam, ronda):
    subclave = clave_bytes.copy()
    while len(subclave) < tam:
        subclave += clave_bytes
    subclave = subclave[:tam]

    pares = list(enumerate(subclave))
    pares.sort(key=lambda x: x[1])
    perm = [i for i, _ in pares]

    k = ronda % tam
    return perm[k:] + perm[:k]

def inversa_perm(perm):
    inv = [0] * len(perm)
    for i, p in enumerate(perm):
        inv[p] = i
    return inv

def aplicar_perm(bloque, perm):
    return [bloque[i] for i in perm]

# ── RONDA DE CIFRADO ──────────────────────────────────────────────────────────

def ronda_cifrado(data_bytes, clave_bytes, ronda):
    """
    Cifra data_bytes en bloques de tamaño variable.
    Usa PKCS#7 en el último bloque para que la operación sea reversible.
    """
    resultado = []
    i = 0
    k_idx = 0

    while i < len(data_bytes):
        tam = (clave_bytes[k_idx % len(clave_bytes)] % 5) + 2
        bloque = list(data_bytes[i:i+tam])

        # PKCS#7: rellenar con el valor del faltante
        if len(bloque) < tam:
            pad = tam - len(bloque)
            bloque += [pad] * pad

        k = clave_bytes[k_idx % len(clave_bytes)]
        bloque = [(x + k + ronda) % MOD for x in bloque]

        perm  = generar_perm(clave_bytes, len(bloque), ronda)
        bloque = aplicar_perm(bloque, perm)

        resultado.extend(bloque)
        i += tam
        k_idx += 1

    return resultado


def ronda_descifrado(data_bytes, clave_bytes, ronda):
    """Inversa exacta de ronda_cifrado."""
    resultado = []
    i = 0
    k_idx = 0

    while i < len(data_bytes):
        tam = (clave_bytes[k_idx % len(clave_bytes)] % 5) + 2
        bloque = list(data_bytes[i:i+tam])
        if len(bloque) < tam:
            bloque += [0] * (tam - len(bloque))

        # Deshacer permutación
        perm  = generar_perm(clave_bytes, len(bloque), ronda)
        inv   = inversa_perm(perm)
        bloque = aplicar_perm(bloque, inv)

        # Deshacer suma
        k = clave_bytes[k_idx % len(clave_bytes)]
        bloque = [(x - k - ronda) % MOD for x in bloque]

        resultado.extend(bloque)
        i += tam
        k_idx += 1

    return resultado

# ── BUFFER DETERMINISTA ───────────────────────────────────────────────────────

def _buffer_para_ronda(seed: str, salt_str: str, ronda: int) -> list:
    """
    Buffer de 256 bytes generado solo con seed+salt+ronda.
    Es independiente de los datos, por lo que el XOR es trivialmente reversible.
    """
    semilla = texto_a_bytes(seed + salt_str + str(ronda))
    return [(semilla[i % len(semilla)] ^ i ^ ronda) % 256 for i in range(256)]


def _mezclar(data_bytes, buffer):
    """XOR con buffer fijo. Su propia inversa."""
    return [(data_bytes[i] ^ buffer[i % len(buffer)]) % MOD
            for i in range(len(data_bytes))]

# ── CIFRADO SIMÉTRICO CCAR ────────────────────────────────────────────────────

def ccar_cifrar(texto: str, seed: str) -> tuple[str, str]:
    """
    Cifra un texto y retorna (cifrado_hex, salt_hex).
    Guarda ambos valores para poder descifrar luego.
    """
    salt     = os.urandom(8)
    salt_str = salt.hex()

    data = texto_a_bytes(texto)
    # Header con la longitud original (4 bytes, big-endian)
    # Necesario para quitar el padding PKCS#7 al descifrar
    header = list(len(data).to_bytes(4, "big"))
    data   = header + data

    estados_previos = []   # data[:4] antes de cada ronda (para reconstruir claves al descifrar)

    for i in range(50):
        estados_previos.append(data[:4])
        estado      = bytes_a_texto(data[:4])
        clave       = seed + salt_str + str(i) + estado
        clave_bytes = texto_a_bytes(clave)
        data        = ronda_cifrado(data, clave_bytes, i)
        data        = _mezclar(data, _buffer_para_ronda(seed, salt_str, i))

    # Los 200 bytes de estados se preijan al cifrado para que descifrar sea posible
    estados_flat = []
    for e in estados_previos:
        estados_flat.extend(e)

    return bytes_a_hex(estados_flat + data), salt_str


def ccar_descifrar(cifrado_hex: str, seed: str, salt_str: str) -> str:
    """
    Descifra un texto previamente cifrado con ccar_cifrar.
    Retorna el texto original.
    """
    payload = hex_a_bytes(cifrado_hex)

    # Separar los 200 bytes de estados del cifrado real
    estados_flat = payload[:200]
    data         = payload[200:]
    estados      = [estados_flat[i*4:(i+1)*4] for i in range(50)]

    # Deshacer rondas en orden inverso
    for i in range(49, -1, -1):
        # Deshacer mezcla (XOR es su propia inversa)
        data = _mezclar(data, _buffer_para_ronda(seed, salt_str, i))

        # Reconstruir clave con el estado guardado
        estado      = bytes_a_texto(estados[i])
        clave       = seed + salt_str + str(i) + estado
        clave_bytes = texto_a_bytes(clave)

        data = ronda_descifrado(data, clave_bytes, i)

    # Recuperar longitud original y quitar header + padding
    longitud_original = int.from_bytes(bytes(data[:4]), "big")
    data = data[4:][:longitud_original]

    return bytes(data).decode("utf-8")

# ── HASH CCAR (sin cambios respecto al original) ──────────────────────────────

def ccar_hash(password: str, seed: str) -> tuple[str, str]:
    """
    Genera un hash CCAR del texto dado.
    Retorna (hash_hex, salt_hex).
    El salt es aleatorio y debe guardarse junto al hash para verificar.
    """
    salt     = os.urandom(8)
    salt_str = salt.hex()

    texto  = password + salt_str
    data   = texto_a_bytes(texto)
    buffer = [i % 256 for i in range(256)]

    for i in range(50):
        estado      = bytes_a_texto(data[:4])
        clave       = seed + str(i) + estado
        clave_bytes = texto_a_bytes(clave)
        data        = ronda_cifrado(data, clave_bytes, i)
        data        = mezclar_buffer(data, buffer)

    return bytes_a_hex(data), salt_str


def ccar_verificar(password: str, seed: str, salt: str, hash_guardado: str) -> bool:
    """Verifica si el texto coincide con un hash CCAR previamente generado."""
    texto  = password + salt
    data   = texto_a_bytes(texto)
    buffer = [i % 256 for i in range(256)]

    for i in range(50):
        estado      = bytes_a_texto(data[:4])
        clave       = seed + str(i) + estado
        clave_bytes = texto_a_bytes(clave)
        data        = ronda_cifrado(data, clave_bytes, i)
        data        = mezclar_buffer(data, buffer)

    return bytes_a_hex(data) == hash_guardado


def mezclar_buffer(data_bytes, buffer):
    for i in range(len(data_bytes)):
        data_bytes[i] = (data_bytes[i] ^ buffer[i % len(buffer)]) % MOD
        buffer[i % len(buffer)] = (buffer[i % len(buffer)] + data_bytes[i]) % MOD
    return data_bytes