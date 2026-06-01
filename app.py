from datetime import datetime
from pathlib import Path
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

# 1. Configuración Estricta de Carpetas (Solución al error TemplateNotFound)
BASE_DIR = Path(__file__).resolve().parent
UPLOAD_FOLDER = BASE_DIR / "uploads"
TEMPLATES_FOLDER = BASE_DIR / "templates"  # Forzamos la ruta absoluta a templates
ALLOWED_EXTENSIONS = {"gcode", "gco", "stl"}

UPLOAD_FOLDER.mkdir(exist_ok=True)

# Pasamos explícitamente a Flask la ubicación real de tu carpeta de plantillas HTML
app = Flask(__name__, template_folder=str(TEMPLATES_FOLDER))
app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)
app.secret_key = "unab-clave-secreta-y-segura"

# 2. Configuración de Base de Datos (SQLite)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{BASE_DIR / 'database.db'}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


# 3. Modelos de la Base de Datos
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    credits = db.Column(db.Integer, default=100)
    files = db.relationship("PrintFile", backref="owner", lazy=True)


class PrintFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(150), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)


# 4. Función de Validación de Archivos
def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


# ==========================================
# RUTAS DE AUTENTICACIÓN
# ==========================================

@app.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("index"))

    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password")

        user_exists = User.query.filter_by(username=username).first()
        if user_exists:
            flash("El nombre de usuario ya está registrado.")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password_hash=hashed_password)

        db.session.add(new_user)
        db.session.commit()

        flash("Registro exitoso. Ahora puedes iniciar sesión.")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("index"))

    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            session["user_id"] = user.id
            session["username"] = user.username
            flash(f"¡Bienvenido de vuelta, {user.username}!")
            return redirect(url_for("index"))

        flash("Usuario o contraseña incorrectos.")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Has cerrado sesión correctamente.")
    return redirect(url_for("login"))


# ==========================================
# RUTAS DEL PORTAL
# ==========================================

@app.route("/")
def index():
    # Si no hay un id en la sesión, directo al login
    if "user_id" not in session:
        return redirect(url_for("login"))

    current_user = User.query.get(session["user_id"])

    # SEGURIDAD NUEVA: Si la sesión tiene un ID pero el usuario ya no existe en la BD
    if current_user is None:
        session.clear()  # Limpiamos la sesión fantasma
        return redirect(url_for("login"))

    # Si todo está bien, traemos sus archivos
    archivos = (
        PrintFile.query.filter_by(user_id=current_user.id)
        .order_by(PrintFile.uploaded_at.desc())
        .all()
    )
    return render_template("index.html", user=current_user, archivos=archivos)


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if "user_id" not in session:
        return redirect(url_for("login"))

    current_user = User.query.get(session["user_id"])

    if request.method == "POST":
        if "print_file" not in request.files:
            flash("No se encontró la parte del archivo.")
            return redirect(request.url)

        file = request.files["print_file"]
        if file.filename == "":
            flash("Por favor, selecciona un archivo válido.")
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(Path(app.config["UPLOAD_FOLDER"]) / filename)

            nuevo_archivo = PrintFile(
                filename=filename, user_id=current_user.id
            )
            db.session.add(nuevo_archivo)
            db.session.commit()

            flash(f"Archivo subido y registrado con éxito: {filename}")
            return redirect(url_for("upload"))

        flash("Tipo de archivo no válido. Usa .gcode, .gco o .stl")
        return redirect(request.url)

    archivos = (
        PrintFile.query.filter_by(user_id=current_user.id)
        .order_by(PrintFile.uploaded_at.desc())
        .all()
    )
    return render_template("upload.html", user=current_user, archivos=archivos)


@app.route("/delete/<int:file_id>", methods=["POST"])
def delete_file(file_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    archivo = PrintFile.query.filter_by(
        id=file_id, user_id=session["user_id"]
    ).first_or_404()

    try:
        file_path = Path(app.config["UPLOAD_FOLDER"]) / archivo.filename
        if file_path.exists():
            file_path.unlink()

        db.session.delete(archivo)
        db.session.commit()
        flash(f"El archivo '{archivo.filename}' fue eliminado con éxito.")
    except Exception:
        db.session.rollback()
        flash("Ocurrió un error inesperado al intentar borrar el archivo.")

    return redirect(request.referrer or url_for("index"))


# Creación de tablas
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)