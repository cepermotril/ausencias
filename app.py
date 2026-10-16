from flask import Flask, render_template, request, redirect, url_for, session, flash
import json, os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "clave_secreta_cep_luis_braille_2026"

PROFESORADO = {
    "75570005D": "Aguilera Garcia, Guillermo Antares",
    "23798721T": "Béjar Pretel, Francisco",
    "76441734S": "Escudero Casado, Alicia",
    "76067037B": "Fernández Delgado, Cristina",
    "74735901T": "Fernandez Rodríguez, Lorena",
    "74724837E": "Fernandez Ruiz, Cándido",
    "23801814B": "García Prados, Felicidad",
    "30255073E": "Hinojosa Ávila, Antonio Luis",
    "44253099H": "Jiménez Vázquez, Vanesa",
    "77693240E": "Montañés Ruiz, Paula",
    "77128726C": "Muñoz Morillas, Natalia",
    "74655932W": "Ortega Miranda, María Carmen",
    "24251143N": "Ortiz Marfil, Fernando",
    "71355595G": "Perales Arias, Ana",
    "33489451W": "Piera Llorens, Eva María",
    "23791734M": "Prados Prados, Teresa",
    "74687117E": "Romero Lozano, Mario Jesús",
    "74650659L": "Sánchez Vázquez, Fermín",
    "23802110P": "Serrano Alcalde, José Luis",
    "77136105Q": "Tovar Calvente, Leticia",
}

DNI_VISITA = ("ALUMNADO27", "MOTRIL", "CEPER", "CEPERMOTRIL", "USUARIO", "1234", "COLEGIO")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARCHIVO  = os.path.join(BASE_DIR, "bajas.json")
HORARIOS = os.path.join(BASE_DIR, "horarios.json")


# ============================================================
#  UTILIDADES
# ============================================================
def cargar_bajas():
    if not os.path.exists(ARCHIVO):
        return []
    with open(ARCHIVO, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def guardar_bajas(bajas):
    with open(ARCHIVO, "w", encoding="utf-8") as f:
        json.dump(bajas, f, ensure_ascii=False, indent=2)


def cargar_horarios():
    if not os.path.exists(HORARIOS):
        return {}
    with open(HORARIOS, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def grupos_de_hoy(dni):
    horarios = cargar_horarios()
    if dni not in horarios:
        return ""
    dias = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]
    hoy = dias[datetime.now().weekday()]
    return horarios[dni].get(hoy, "")


def fecha_bonita():
    dias  = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", "Domingo"]
    meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
             "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    hoy = datetime.now()
    return f"{dias[hoy.weekday()]}, {hoy.day} de {meses[hoy.month-1]} de {hoy.year}"


def baja_activa(b):
    """Devuelve True si la baja sigue activa hoy."""
    fi = b.get("fecha_incorp", "").strip()
    if not fi:
        return True  # Sin fecha de incorporación = activa indefinidamente
    try:
        fecha_inc = datetime.strptime(fi, "%Y-%m-%d").date()
        return fecha_inc >= datetime.now().date()
    except ValueError:
        return True  # Formato raro â†’ mostramos por seguridad


# ============================================================
#  LOGIN
# ============================================================
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        dni = request.form.get("dni", "").strip().upper()

        if dni in DNI_VISITA:
            session["rol"]    = "Visita"
            session["nombre"] = "Alumnado"
            session["user"]   = "Visita"
            return redirect(url_for("index"))

        if dni in PROFESORADO:
            session["rol"]    = "maestro"
            session["nombre"] = PROFESORADO[dni]
            session["user"]   = dni
            return redirect(url_for("index"))

        flash("Contrasena incorrecta")

    return render_template("login.html")


# ============================================================
#  LISTA DE BAJAS ACTIVAS
# ============================================================
@app.route("/bajas")
def index():
    if "rol" not in session:
        return redirect(url_for("login"))

    todas = cargar_bajas()

    # Solo mostramos las que siguen activas
    bajas_activas = [b for b in todas if baja_activa(b)]

    # Quitar duplicados por usuario (nos quedamos con la más reciente)
    vistos = {}
    for b in bajas_activas:
        vistos[b["user"]] = b  # el último sobreescribe
    bajas_activas = list(vistos.values())

    bajas_activas.sort(key=lambda b: b["nombre"])

    return render_template("index.html",
                           bajas=bajas_activas,
                           rol=session["rol"],
                           nombre=session.get("nombre"),
                           user=session.get("user"),
                           fecha_hoy=fecha_bonita())


# ============================================================
#  NUEVA BAJA
# ============================================================
@app.route("/nueva", methods=["GET", "POST"])
def nueva():
    if session.get("rol") != "maestro":
        return redirect(url_for("login"))

    if request.method == "POST":
        grupos       = request.form.get("grupos", "").strip()
        fecha_incorp = request.form.get("fecha_incorp", "").strip()

        if not grupos:
            flash("Indica al menos un grupo")
            return redirect(url_for("nueva"))

        bajas = cargar_bajas()

        # Eliminar cualquier baja previa del mismo maestro
        bajas = [b for b in bajas if b["user"] != session["user"]]

        bajas.append({
            "fecha_registro": datetime.now().strftime("%d/%m/%Y"),
            "user":           session["user"],
            "nombre":         session["nombre"],
            "grupos":         grupos,
            "fecha_incorp":   fecha_incorp,
        })
        guardar_bajas(bajas)
        return redirect(url_for("index"))

    grupos_hoy = grupos_de_hoy(session["user"])
    return render_template("nueva.html",
                           nombre=session["nombre"],
                           fecha_hoy=fecha_bonita(),
                           grupos_hoy=grupos_hoy)


# ============================================================
#  BORRAR BAJA (ya me he incorporado)
# ============================================================
@app.route("/borrar/<user>", methods=["POST"])
def borrar(user):
    if session.get("rol") != "maestro" or user != session["user"]:
        return redirect(url_for("login"))

    bajas = cargar_bajas()
    # Borrar TODAS las bajas del maestro (se ha incorporado)
    bajas = [b for b in bajas if b["user"] != user]
    guardar_bajas(bajas)
    return redirect(url_for("index"))


# ============================================================
#  LOGOUT
# ============================================================
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ============================================================
#  ARRANQUE
# ============================================================
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
