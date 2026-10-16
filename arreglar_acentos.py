# arreglar_acentos.py
with open("app.py", "rb") as f:
    datos = f.read()

# Reemplazos directos de bytes (los "malos" son secuencias UTF-8 de caracteres Latin-1)
reemplazos = {
    b"\xc3\x83\xc2\xa1": b"\xc3\xa1",  # Ã¡ -> á
    b"\xc3\x83\xc2\xa9": b"\xc3\xa9",  # Ã© -> é
    b"\xc3\x83\xc2\xad": b"\xc3\xad",  # Ã -> í
    b"\xc3\x83\xc2\xb3": b"\xc3\xb3",  # Ã³ -> ó
    b"\xc3\x83\xc2\xba": b"\xc3\xba",  # Ãº -> ú
    b"\xc3\x83\xc2\xb1": b"\xc3\xb1",  # Ã± -> ñ
    b"\xc3\x83\xc2\x81": b"\xc3\x81",  # Ã -> Á
    b"\xc3\x83\xc2\x89": b"\xc3\x89",  # Ã -> É
}

for malo, bueno in reemplazos.items():
    datos = datos.replace(malo, bueno)

with open("app.py", "wb") as f:
    f.write(datos)

print("OK - Acabado.")
