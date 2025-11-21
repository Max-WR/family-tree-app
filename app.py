from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime

app = Flask(__name__)

# Database config - Use PostgreSQL if available, otherwise SQLite for local development
if os.environ.get('DATABASE_URL'):
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace('postgres://', 'postgresql://')
else:
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
    name = db.Column(db.String(200), nullable=False)
    birth_year = db.Column(db.String(20))
    death_year = db.Column(db.String(20))
    bio_text = db.Column(db.Text)
    profile_photo = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Media(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'))
    media_type = db.Column(db.String(50))
    file_path = db.Column(db.String(300))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Relationship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('person.id'))
    child_id = db.Column(db.Integer, db.ForeignKey('person.id'))
    relationship_type = db.Column(db.String(50), default='biological')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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
            import uuid
            ext = photo.filename.rsplit('.', 1)[1].lower() if '.' in photo.filename else ''
            unique_filename = f"{uuid.uuid4().hex}.{ext}" if ext else f"{uuid.uuid4().hex}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            photo.save(filepath)
            # Store relative path
            filename = f"static/uploads/{unique_filename}"

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

def create_app():
    with app.app_context():
        db.create_all()
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)