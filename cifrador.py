# -*- coding: utf-8 -*-
"""
Algoritmo CCAR — Hash con salt automático
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
    resultado = []
    i = 0
    k_idx = 0

    while i < len(data_bytes):
        tam = (clave_bytes[k_idx % len(clave_bytes)] % 5) + 2
        bloque = data_bytes[i:i+tam]

        if len(bloque) < tam:
            bloque += [0] * (tam - len(bloque))

        k = clave_bytes[k_idx % len(clave_bytes)]
        bloque = [(x + k + ronda) % MOD for x in bloque]

        perm = generar_perm(clave_bytes, len(bloque), ronda)
        bloque = aplicar_perm(bloque, perm)

        resultado.extend(bloque)
        i += tam
        k_idx += 1

    return resultado

# ── MEZCLA CON BUFFER ─────────────────────────────────────────────────────────

def mezclar_buffer(data_bytes, buffer):
    for i in range(len(data_bytes)):
        data_bytes[i] = (data_bytes[i] ^ buffer[i % len(buffer)]) % MOD
        buffer[i % len(buffer)] = (buffer[i % len(buffer)] + data_bytes[i]) % MOD
    return data_bytes

# ── HASH CCAR (pública) ───────────────────────────────────────────────────────

def ccar_hash(password: str, seed: str) -> tuple[str, str]:
    """
    Genera un hash CCAR del texto dado.
    Retorna (hash_hex, salt_hex).
    El salt es aleatorio y debe guardarse junto al hash para verificar.
    """
    salt = os.urandom(8)
    salt_str = salt.hex()

    texto = password + salt_str
    data = texto_a_bytes(texto)
    buffer = [i % 256 for i in range(256)]

    for i in range(50):
        estado = bytes_a_texto(data[:4])
        clave = seed + str(i) + estado
        clave_bytes = texto_a_bytes(clave)
        data = ronda_cifrado(data, clave_bytes, i)
        data = mezclar_buffer(data, buffer)

    return bytes_a_hex(data), salt_str


def ccar_verificar(password: str, seed: str, salt: str, hash_guardado: str) -> bool:
    """
    Verifica si el texto coincide con un hash CCAR previamente generado.
    """
    texto = password + salt
    data = texto_a_bytes(texto)
    buffer = [i % 256 for i in range(256)]

    for i in range(50):
        estado = bytes_a_texto(data[:4])
        clave = seed + str(i) + estado
        clave_bytes = texto_a_bytes(clave)
        data = ronda_cifrado(data, clave_bytes, i)
        data = mezclar_buffer(data, buffer)

    return bytes_a_hex(data) == hash_guardado