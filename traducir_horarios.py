# traducir_horarios.py
import json

TRADUCCIONES = {
    "EOI PAT":    "Escuela Idiomas Patrimonio",
    "AUX":        "Auxiliar Enfermería",
    "TIC":        "Informática",
    "INT":        "Español para Extranjeros",
    "INTER":      "Español para Extranjeros",
    "PAT":        "Patrimonio",
    "ING":        "Inglés",
    "VC":         "Virgen de la Cabeza",
    "PL":         "Prueba Libre",
    "FR":         "Francés",
    "HS":         "Hábitos Sanos",
    "PAU":        "Acceso Universidad",
    "CFGS":       "Grado Superior",
    "TOR":        "Torrenueva",
    "CAL":        "Calahonda",
    "VAR":        "Varadero",
    "CAR":        "Carchuna",
    "CL":         "Club de Lectura",
    "EC":         "Escritura Creativa",
    "EOI":        "Escuela Idiomas",
    "MAYORES 55": None,
    "GS":         "Grado Superior",
    "ZAF":        "Zafra",
}

# Estas cadenas NO se traducen aunque empiecen por una clave del diccionario
EXCEPCIONES = ["TIC TAE"]


def traducir_asignatura(texto):
    texto = texto.strip()
    if not texto:
        return None

    # Si empieza por una excepción, devolver tal cual
    for exc in EXCEPCIONES:
        if texto == exc or texto.startswith(exc + " "):
            return texto

    for clave in sorted(TRADUCCIONES.keys(), key=len, reverse=True):
        if texto == clave:
            return TRADUCCIONES[clave]
        if texto.startswith(clave + " "):
            traduccion = TRADUCCIONES[clave]
            if traduccion is None:
                return None
            resto = texto[len(clave):].strip()
            return f"{traduccion} {resto}".strip()
    return texto


def traducir_dia(dia_texto):
    if not dia_texto:
        return dia_texto
    partes = [p.strip() for p in dia_texto.split(",")]
    nuevas = []
    for p in partes:
        t = traducir_asignatura(p)
        if t is not None:
            nuevas.append(t)
    return ", ".join(nuevas)


with open("horarios.json", "r", encoding="utf-8-sig") as f:
    datos = json.load(f)

for dni, info in datos.items():
    for dia in ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]:
        if dia in info:
            info[dia] = traducir_dia(info[dia])

with open("horarios.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(datos, f, ensure_ascii=False, indent=2)

print("OK - Traduccion completada.")