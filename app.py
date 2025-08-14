from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from validators import email as email_validator

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Change this in production

# SQLite config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Student Model
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    roll_no = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    age = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<Student {self.name}>"



@app.route('/')
def index():
    students = Student.query.all()
    return render_template('index.html', students=students)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name'].strip()
        roll_no = request.form['roll_no'].strip()
        email = request.form['email'].strip()
        age = request.form['age'].strip()

        if not email_validator(email):
            flash('Invalid email address.', 'danger')
            return redirect(url_for('register'))

        if not age.isdigit() or int(age) <= 0:
            flash('Age must be a positive number.', 'danger')
            return redirect(url_for('register'))

        # Check uniqueness
        if Student.query.filter_by(roll_no=roll_no).first():
            flash('Roll number already exists.', 'danger')
            return redirect(url_for('register'))
        if Student.query.filter_by(email=email).first():
            flash('Email already exists.', 'danger')
            return redirect(url_for('register'))

        try:
            student = Student(name=name, roll_no=roll_no, email=email, age=int(age))
            db.session.add(student)
            db.session.commit()
            flash('Student registered successfully!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error: {str(e)}", 'danger')
            return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/view/<int:id>')
def view(id):
    student = Student.query.get_or_404(id)
    return render_template('view.html', student=student)

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    student = Student.query.get_or_404(id)

    if request.method == 'POST':
        name = request.form['name'].strip()
        roll_no = request.form['roll_no'].strip()
        email = request.form['email'].strip()
        age = request.form['age'].strip()

        if not email_validator(email):
            flash('Invalid email address.', 'danger')
            return redirect(url_for('update', id=id))

        if not age.isdigit() or int(age) <= 0:
            flash('Age must be a positive number.', 'danger')
            return redirect(url_for('update', id=id))

        # Check for uniqueness excluding current student
        existing_roll = Student.query.filter(Student.roll_no == roll_no, Student.id != id).first()
        if existing_roll:
            flash('Roll number already exists.', 'danger')
            return redirect(url_for('update', id=id))

        existing_email = Student.query.filter(Student.email == email, Student.id != id).first()
        if existing_email:
            flash('Email already exists.', 'danger')
            return redirect(url_for('update', id=id))

        try:
            student.name = name
            student.roll_no = roll_no
            student.email = email
            student.age = int(age)
            db.session.commit()
            flash('Student updated successfully!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error: {str(e)}", 'danger')

    return render_template('update.html', student=student)

@app.route('/delete/<int:id>')
def delete(id):
    student = Student.query.get_or_404(id)
    try:
        db.session.delete(student)
        db.session.commit()
        flash('Student deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"Error: {str(e)}", 'danger')
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run()

