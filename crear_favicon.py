from PIL import Image, ImageDraw
import os

ENTRADA = "static/logo.jpg"
SALIDA  = "static/favicon.png"
TAMANO  = 128

print(f"Leyendo: {ENTRADA}")
img = Image.open(ENTRADA).convert("RGBA")

# 1. Recortar al centro cuadrado
w, h = img.size
lado = min(w, h)
izq = (w - lado) // 2
sup = (h - lado) // 2
img = img.crop((izq, sup, izq + lado, sup + lado))

# 2. Redimensionar
img = img.resize((TAMANO, TAMANO), Image.LANCZOS)

# 3. Mascara circular (un poco mas pequena para que se vea el anillo)
mascara = Image.new("L", (TAMANO, TAMANO), 0)
dibujo = ImageDraw.Draw(mascara)
dibujo.ellipse((0, 0, TAMANO - 1, TAMANO - 1), fill=255)

# 4. Aplicar la mascara
img.putalpha(mascara)

# 5. Guardar
img.save(SALIDA, "PNG")
print(f"Guardado: {SALIDA} ({os.path.getsize(SALIDA)} bytes)")

# 6. Tambien .ico
ICO = "static/favicon.ico"
img.save(ICO, sizes=[(16,16),(32,32),(48,48),(64,64)])
print(f"Guardado: {ICO} ({os.path.getsize(ICO)} bytes)")
