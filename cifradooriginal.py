import os
MOD = 256

# --- UTILIDADES ---
def texto_a_bytes(texto):
    return list(texto.encode("utf-8"))

def bytes_a_texto(lista):
    return bytes(lista).decode("utf-8", errors="ignore")

def bytes_a_hex(lista):
    return ''.join(format(b, '02x') for b in lista)

# --- PERMUTACION DINAMICA ---
def generar_perm(clave_bytes, tam, ronda):
  #Genera un orden de reordenamiento para un bloque de bytes
    subclave = clave_bytes.copy()
    while len(subclave) < tam:
        subclave += clave_bytes
    subclave = subclave[:tam]

    pares = list(enumerate(subclave))
    pares.sort(key=lambda x: x[1])  #Ordena esos pares por el valor

    # def obtener_segundo(x):
    #   return x[1]
    # pares.sort(key=obtener_segundo)

    perm = [i for i, _ in pares]

    k = ronda % tam
    nueva_perm = perm[k:] + perm[:k]

    if ronda < 2: # Solo printeamos en las primeras rondas para ejemplo
        print(f"      [Permutación] Tamaño bloque: {tam} -> Patrón generado: {nueva_perm}")

    return nueva_perm

def aplicar_perm(bloque, perm):
    return [bloque[i] for i in perm]

# --- CIFRADO BASE (UNA RONDA) ---
def ronda_cifrado(data_bytes, clave_bytes, ronda):
  #Procesa el mensaje completo bloque por bloque - el tamaño del bloque es dinámico
    resultado = []
    i = 0
    k_idx = 0

    if ronda < 2:
        print(f"\n  --- Iniciando Ronda de Cifrado #{ronda} ---")
        print(f"  Data entrante (primeros 15 bytes): {data_bytes[:15]}...")

    while i < len(data_bytes):
        # El tamaño del bloque cambia dinámicamente según la clave
        tam = (clave_bytes[k_idx % len(clave_bytes)] % 5) + 2
        bloque = data_bytes[i:i+tam]

        # Padding (relleno con ceros si el último bloque es corto)
        if len(bloque) < tam:
            bloque += [0]*(tam - len(bloque))

        k = clave_bytes[k_idx % len(clave_bytes)]

        if ronda < 2 and i == 0: # Imprimimos solo el primer bloque de la ronda como muestra
            print(f"    -> Bloque #0 original: {bloque} (Tamaño dinámico: {tam})")

        # 1. Suma modular
        bloque = [(x + k + ronda) % MOD for x in bloque]
        #Desplazamiento/suma modular — equivale a un cifrado César por byte
        if ronda < 2 and i == 0:
            print(f"    -> Bloque #0 tras Suma Modular (XOR/Suma con clave y ronda): {bloque}")

        # 2. Permutación
        perm = generar_perm(clave_bytes, len(bloque), ronda)
        bloque = aplicar_perm(bloque, perm) #Reordena los bytes según la permutación generada

        if ronda < 2 and i == 0:
            print(f"    -> Bloque #0 final tras Permutación: {bloque}")

        resultado.extend(bloque)
        i += tam
        k_idx += 1

    return resultado

# --- BUFFER PEQUEÑO (MEZCLA) ---
def mezclar_buffer(data_bytes, buffer):
    # Esta función hace que el estado actual dependa de un histórico (el buffer)
    primeros_cambios_data = []
    primeros_cambios_buff = []

    for i in range(len(data_bytes)):
        orig_data = data_bytes[i]
        orig_buff = buffer[i % len(buffer)]

        # Mezcla usando operación XOR
        data_bytes[i] = (data_bytes[i] ^ buffer[i % len(buffer)]) % MOD
        # Retroalimentación: modificamos el buffer con el nuevo byte de data
        buffer[i % len(buffer)] = (buffer[i % len(buffer)] + data_bytes[i]) % MOD

        if i < 3: # Guardamos una muestra de los 3 primeros bytes mezclados
            primeros_cambios_data.append(f"{orig_data}->{data_bytes[i]}")
            primeros_cambios_buff.append(f"{orig_buff}->{buffer[i % len(buffer)]}")

    return data_bytes

# --- PSEUDO HASH ---
def pseudo_hash(password, seed):
    print("\n[PROCESO] Generando Salt aleatorio...")
    salt = os.urandom(8)
    salt_str = salt.hex()
    print(f"[PROCESO] Salt generado (hex): {salt_str}")

    texto = password + salt_str
    data = texto_a_bytes(texto)
    print(f"[PROCESO] Entrada combinada (Password + Salt) en bytes:\n  {data}")

    buffer = [i % 256 for i in range(256)]
    rondas = 50

    print(f"\n[PROCESO] Iniciando bucle de {rondas} rondas de difusión...")
    for i in range(rondas):
        # El estado toma los primeros 4 bytes para alterar la clave de la siguiente ronda
        estado = bytes_a_texto(data[:4])
        clave = seed + str(i) + estado
        clave_bytes = texto_a_bytes(clave)

        if i < 2:
            print(f"\n=== RONDA {i} ===")
            print(f"  Clave dinámica generada: \"{clave}\"")

        # Ejecutar transformaciones
        data = ronda_cifrado(data, clave_bytes, i)
        data = mezclar_buffer(data, buffer)

        if i < 2:
            print(f"  Estado de 'data' al terminar ronda {i} (primeros 15 bytes): {data[:15]}...")

    print("\n[PROCESO] Rondas finalizadas. Convirtiendo bytes resultantes a Hexadecimal...")
    hash_hex = bytes_a_hex(data)
    return hash_hex, salt_str

# --- VERIFICACION (LOGIN) ---
def verificar(password, seed, salt_guardado, hash_guardado):
    print("\n[VERIFICACIÓN] Iniciando proceso de login...")
    texto = password + salt_guardado
    data = texto_a_bytes(texto)
    print(f"[VERIFICACIÓN] Reconstruyendo entrada con salt guardado:\n  {data}")

    buffer = [i % 256 for i in range(256)]

    # Mismo proceso exacto sin prints detallados (ya sabemos cómo funciona internamente)
    for i in range(50):
        estado = bytes_a_texto(data[:4])
        clave = seed + str(i) + estado
        clave_bytes = texto_a_bytes(clave)
        data = ronda_cifrado(data, clave_bytes, i)
        data = mezclar_buffer(data, buffer)

    hash_login = bytes_a_hex(data)
    print(f"[VERIFICACIÓN] Hash resultante del intento de Login: {hash_login}")
    print(f"[VERIFICACIÓN] Hash guardado en el sistema:          {hash_guardado}")

    return hash_login == hash_guardado

# --- DEMO ---
if __name__ == "__main__":
    seed = "CLAVE_SECRETA_DEL_SISTEMA"

    print("=== REGISTRO ===")
    password = input("Contraseña para registrar: ")

    hash_val, salt = pseudo_hash(password, seed)

    print("\n=== RESULTADO DEL REGISTRO ===")
    print(f"Hash final: {hash_val}")
    print(f"Salt usado: {salt}")

    print("\n=== LOGIN ===")
    password_login = input("Introduce contraseña para iniciar sesión: ")

    if verificar(password_login, seed, salt, hash_val):
        print("\n[RESULTADO] >>> Acceso correcto ✔ <<<")
    else:
        print("\n[RESULTADO] >>> Acceso denegado ✗ <<<")