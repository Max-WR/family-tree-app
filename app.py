from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Database config - FIXED VERSION
if 'DATABASE_URL' in os.environ:
    database_url = os.environ['DATABASE_URL'].replace('postgres://', 'postgresql://')
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///family.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize db FIRST, before defining models
db = SQLAlchemy(app)

# UPLOAD folder
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
    try:
        people = Person.query.order_by(Person.name).all()
        return render_template("index.html", people=people)
    except Exception as e:
        return f"Error loading people: {str(e)}"

@app.route("/add_person", methods=["GET", "POST"])
def add_person():
    if request.method == "POST":
        try:
            name = request.form.get("name", "").strip()
            birth_year = request.form.get("birth_year", "").strip()
            death_year = request.form.get("death_year", "").strip()
            bio_text = request.form.get("bio_text", "").strip()

            photo = request.files.get("profile_photo", None)
            filename = None

            if photo and photo.filename:
                # Save the photo
                filename = os.path.join('static/uploads', photo.filename)
                photo.save(filename)
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
        except Exception as e:
            return f"Error adding person: {str(e)}"

    return render_template("add_person.html")

@app.route("/person/<int:person_id>")
def person_profile(person_id):
    try:
        p = Person.query.get_or_404(person_id)
        media = Media.query.filter_by(person_id=person_id).all()
        return render_template("person_profile.html", person=p, media=media)
    except Exception as e:
        return f"Error loading profile: {str(e)}"

# Initialize database tables
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)