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
    "23801814B": "García Prados, Felicidad ",
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

DNI_VISITA = "ALUMNADO27"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARCHIVO  = os.path.join(BASE_DIR, "bajas.json")

def cargar_bajas():
    if not os.path.exists(ARCHIVO):
        return []
    with open(ARCHIVO, "r", encoding="utf-8") as f:
        return json.load(f)

def guardar_bajas(bajas):
    with open(ARCHIVO, "w", encoding="utf-8") as f:
        json.dump(bajas, f, ensure_ascii=False, indent=2)

def fecha_bonita():
    dias  = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", "Domingo"]
    meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
             "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    hoy = datetime.now()
    return f"{dias[hoy.weekday()]}, {hoy.day} de {meses[hoy.month-1]} de {hoy.year}"

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        dni = request.form.get("dni", "").strip().upper()

        if dni == DNI_VISITA:
            session["rol"]    = "visita"
            session["nombre"] = "Visita"
            session["user"]   = "visita"
            return redirect(url_for("index"))

        if dni in PROFESORADO:
            session["rol"]    = "maestro"
            session["nombre"] = PROFESORADO[dni]
            session["user"]   = dni
            return redirect(url_for("index"))

        flash("Contrasena incorrecta")

    return render_template("login.html")

@app.route("/bajas")
def index():
    if "rol" not in session:
        return redirect(url_for("login"))

    hoy_str = datetime.now().strftime("%d/%m/%Y")
    todas = cargar_bajas()
    bajas_hoy = [b for b in todas if b["fecha_registro"] == hoy_str]
    bajas_hoy.sort(key=lambda b: b["nombre"])

    return render_template("index.html", bajas=bajas_hoy, rol=session["rol"],
                           nombre=session.get("nombre"), user=session.get("user"),
                           fecha_hoy=fecha_bonita())

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

        hoy_str = datetime.now().strftime("%d/%m/%Y")

        bajas = cargar_bajas()
        bajas = [b for b in bajas if not (b["fecha_registro"] == hoy_str
                                          and b["user"] == session["user"])]

        bajas.append({
            "fecha_registro": hoy_str,
            "user":           session["user"],
            "nombre":         session["nombre"],
            "grupos":         grupos,
            "fecha_incorp":   fecha_incorp,
        })
        guardar_bajas(bajas)
        return redirect(url_for("index"))

    return render_template("nueva.html", nombre=session["nombre"], fecha_hoy=fecha_bonita())

@app.route("/borrar/<user>", methods=["POST"])
def borrar(user):
    if session.get("rol") != "maestro" or user != session["user"]:
        return redirect(url_for("login"))

    hoy_str = datetime.now().strftime("%d/%m/%Y")
    bajas = cargar_bajas()
    bajas = [b for b in bajas if not (b["fecha_registro"] == hoy_str and b["user"] == user)]
    guardar_bajas(bajas)
    return redirect(url_for("index"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
