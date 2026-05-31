from pathlib import Path
from flask import Flask, flash, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_FOLDER = BASE_DIR / "uploads"
ALLOWED_EXTENSIONS = {"gcode", "gco"}

UPLOAD_FOLDER.mkdir(exist_ok=True)

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)
app.secret_key = "replace-with-a-secure-key"


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        if "print_file" not in request.files:
            flash("No file part in the form.")
            return redirect(request.url)

        file = request.files["print_file"]
        if file.filename == "":
            flash("Please choose a file to upload.")
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(Path(app.config["UPLOAD_FOLDER"]) / filename)
            flash(f"Upload successful: {filename}")
            return redirect(url_for("upload"))

        flash("Invalid file type. Please upload a .gcode or .gco file.")
        return redirect(request.url)

    return render_template("upload.html")


if __name__ == "__main__":
    app.run(debug=True)
