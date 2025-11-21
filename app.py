from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Database config - SIMPLEST VERSION
if 'DATABASE_URL' in os.environ:
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///family.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_recycle': 300,
    'pool_pre_ping': True
}

db = SQLAlchemy(app)

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
        return f"Error: {str(e)}"

@app.route("/add_person", methods=["GET", "POST"])
def add_person():
    if request.method == "POST":
        try:
            name = request.form.get("name", "").strip()
            new_person = Person(
                name=name,
                birth_year=request.form.get("birth_year", "").strip(),
                death_year=request.form.get("death_year", "").strip(),
                bio_text=request.form.get("bio_text", "").strip(),
                profile_photo=None
            )
            db.session.add(new_person)
            db.session.commit()
            return redirect(url_for("index"))
        except Exception as e:
            return f"Error: {str(e)}"
    return render_template("add_person.html")

@app.route("/person/<int:person_id>")
def person_profile(person_id):
    try:
        p = Person.query.get_or_404(person_id)
        return render_template("person_profile.html", person=p, media=[])
    except Exception as e:
        return f"Error: {str(e)}"

# Initialize database
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)