import os

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select

db = SQLAlchemy()


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    course = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "local-development-key")
    database_url = os.getenv("DATABASE_URL", "sqlite:///students.db")
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+psycopg://", 1)
    elif database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    @app.get("/")
    def index():
        students = db.session.scalars(select(Student).order_by(Student.name)).all()
        return render_template("index.html", students=students)

    @app.route("/students/new", methods=["GET", "POST"])
    def create_student():
        if request.method == "POST":
            student, error = student_from_form()
            if error:
                flash(error, "error")
                return render_template("student_form.html", student=None)
            db.session.add(student)
            return save_student("Student added successfully.")
        return render_template("student_form.html", student=None)

    @app.route("/students/<int:student_id>/edit", methods=["GET", "POST"])
    def edit_student(student_id):
        student = db.get_or_404(Student, student_id)
        if request.method == "POST":
            updated, error = student_from_form(existing_id=student.id)
            if error:
                flash(error, "error")
                return render_template("student_form.html", student=student)
            student.name = updated.name
            student.email = updated.email
            student.course = updated.course
            student.year = updated.year
            return save_student("Student details updated.")
        return render_template("student_form.html", student=student)

    @app.post("/students/<int:student_id>/delete")
    def delete_student(student_id):
        student = db.get_or_404(Student, student_id)
        db.session.delete(student)
        return save_student("Student removed.")

    def student_from_form(existing_id=None):
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        course = request.form.get("course", "").strip()
        try:
            year = int(request.form.get("year", ""))
        except ValueError:
            return None, "Enter a valid study year."
        if not name or not email or not course:
            return None, "Please complete every field."
        if year < 1 or year > 8:
            return None, "Study year must be between 1 and 8."
        duplicate = db.session.scalar(select(Student).where(Student.email == email))
        if duplicate and duplicate.id != existing_id:
            return None, "That email address is already in use."
        return Student(name=name, email=email, course=course, year=year), None

    def save_student(message):
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            flash("Could not save the student. Check the email and try again.", "error")
        else:
            flash(message, "success")
        return redirect(url_for("index"))

    return app


app = create_app()
