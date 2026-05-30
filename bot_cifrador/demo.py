"""
demo.py — Prueba el cifrador directamente (sin bot)
Correr con: python demo.py
"""

from cifrador import cifrar, descifrar


def prueba(mensaje: str, clave: str, label: str = ""):
    tag = f"[{label}] " if label else ""
    print(f"\n{tag}{'─'*50}")
    print(f"  📝 Mensaje   : {mensaje!r}")
    print(f"  🔑 Clave     : {clave!r}")

    cifrado = cifrar(mensaje, clave)
    print(f"  🔒 Cifrado   : {cifrado}")

    descifrado = descifrar(cifrado, clave)
    ok = descifrado == mensaje
    print(f"  🔓 Descifrado: {descifrado!r}")
    print(f"  {'✅ CORRECTO' if ok else '❌ ERROR — no coincide'}")
    return ok


def prueba_clave_incorrecta(mensaje: str, clave_ok: str, clave_mal: str):
    print(f"\n[CLAVE INCORRECTA] {'─'*38}")
    print(f"  📝 Mensaje        : {mensaje!r}")
    cifrado    = cifrar(mensaje, clave_ok)
    descifrado = descifrar(cifrado, clave_mal)
    print(f"  🔓 Con clave mal  : {descifrado!r}")
    if descifrado != mensaje:
        print("  ✅ Correcto — la clave incorrecta NO descifra el mensaje")
    else:
        print("  ⚠️  Coincidencia inesperada")


if __name__ == "__main__":
    print("=" * 55)
    print("  PRUEBA DEL ALGORITMO DE CIFRADO")
    print("=" * 55)

    resultados = []

    resultados.append(prueba("Hola mundo!",                    "clave123",           "básico"))
    resultados.append(prueba("Mensaje secreto de prueba",      "superClave!2024",    "frase"))
    resultados.append(prueba("Números 12345 y símbolos @#$%",  "abc",                "especiales"))
    resultados.append(prueba("a",                              "x",                  "1 char"))
    resultados.append(prueba("A" * 200,                        "clave_larga_test",   "largo"))
    resultados.append(prueba("Texto con ñ, á, é, ü",           "clave",              "UTF-8"))

    prueba_clave_incorrecta("Mensaje importante", "claveCorrecta", "claveErronea")

    print(f"\n{'='*55}")
    total = len(resultados)
    ok    = sum(resultados)
    print(f"  Resultado: {ok}/{total} pruebas pasadas {'✅' if ok == total else '❌'}")
    print("=" * 55)
