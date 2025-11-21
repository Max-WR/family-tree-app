from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# SIMPLER Database config - no separate folder
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///family.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# UPLOAD folder
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---- DATABASE MODELS ----
class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    birth_year = db.Column(db.String(20))
    death_year = db.Column(db.String(20))
    bio_text = db.Column(db.Text)
    profile_photo = db.Column(db.String(300))

class Media(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'))
    media_type = db.Column(db.String(50))
    file_path = db.Column(db.String(300))
    description = db.Column(db.Text)

# ---- ROUTES ----
@app.route("/")
def index():
    people = Person.query.order_by(Person.name).all()
    return render_template("index.html", people=people)

@app.route("/add_person", methods=["GET", "POST"])
def add_person():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        birth_year = request.form.get("birth_year", "").strip()
        death_year = request.form.get("death_year", "").strip()
        bio_text = request.form.get("bio_text", "").strip()

        photo = request.files.get("profile_photo", None)
        filename = None

        if photo and photo.filename:
            # Save the photo
            filename = os.path.join(app.config['UPLOAD_FOLDER'], photo.filename)
            photo.save(filename)
            # Store relative path
            filename = f"static/uploads/{photo.filename}"

        new_person = Person(
            name=name,
            birth_year=birth_year,
            death_year=death_year,
            bio_text=bio_text,
            profile_photo=filename
        )
        
        db.session.add(new_person)
        db.session.commit()

        return redirect(url_for("index"))

    return render_template("add_person.html")

@app.route("/person/<int:person_id>")
def person_profile(person_id):
    p = Person.query.get_or_404(person_id)
    media = Media.query.filter_by(person_id=person_id).all()
    return render_template("person_profile.html", person=p, media=media)

if __name__ == "__main__":
    # Create DB if not exists
    with app.app_context():
        db.create_all()
    app.run(debug=True)