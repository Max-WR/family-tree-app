from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Debug database connection
print("=== DATABASE DEBUG INFO ===")
if 'DATABASE_URL' in os.environ:
    database_url = os.environ['DATABASE_URL']
    print(f"Database URL found: {database_url[:50]}...")  # Show first 50 chars
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url.replace('postgres://', 'postgresql://')
else:
    print("No DATABASE_URL found, using SQLite")
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///family.db'

print(f"Final database URL: {app.config['SQLALCHEMY_DATABASE_URI'][:50]}...")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

try:
    db = SQLAlchemy(app)
    print("Database connection successful")
except Exception as e:
    print(f"Database connection failed: {e}")

# UPLOAD folder
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ---- SIMPLIFIED DATABASE MODELS ----
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
        print("=== Loading homepage ===")
        people = Person.query.order_by(Person.name).all()
        print(f"Found {len(people)} people in database")
        return render_template("index.html", people=people)
    except Exception as e:
        error_msg = f"Error loading homepage: {str(e)}"
        print(error_msg)
        return error_msg

@app.route("/add_person", methods=["GET", "POST"])
def add_person():
    if request.method == "POST":
        try:
            name = request.form.get("name", "").strip()
            print(f"Adding person: {name}")
            
            new_person = Person(
                name=name,
                birth_year=request.form.get("birth_year", "").strip(),
                death_year=request.form.get("death_year", "").strip(),
                bio_text=request.form.get("bio_text", "").strip(),
                profile_photo=None  # Skip photos for now
            )
            
            db.session.add(new_person)
            db.session.commit()
            print(f"Successfully added: {name}")
            return redirect(url_for("index"))
        except Exception as e:
            error_msg = f"Error adding person: {str(e)}"
            print(error_msg)
            return error_msg

    return render_template("add_person.html")

@app.route("/person/<int:person_id>")
def person_profile(person_id):
    try:
        p = Person.query.get_or_404(person_id)
        return render_template("person_profile.html", person=p, media=[])
    except Exception as e:
        return f"Error loading profile: {str(e)}"

# Initialize database
try:
    with app.app_context():
        print("=== Creating database tables ===")
        db.create_all()
        print("Database tables created successfully")
except Exception as e:
    print(f"Error creating tables: {e}")

if __name__ == "__main__":
    app.run(debug=True)