import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename
import pandas as pd
from datetime import datetime
from config import Config

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), 'Templates'))
app.config.from_object(Config)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
mail = Mail(app)

# --- Models ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    is_admin = db.Column(db.Boolean, default=False)

class Grant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    applicant = db.Column(db.String(150), nullable=False)
    status = db.Column(db.String(50), default='Pending')
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    file_path = db.Column(db.String(300))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    deadline = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text, nullable=True)

# --- Auth ---
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Routes ---
@app.route('/')
@login_required
def index():
    grants = Grant.query.filter_by(user_id=current_user.id if not current_user.is_admin else None).all()
    return render_template('dashboard.html', grants=grants, admin=current_user.is_admin)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.password == request.form['password']:
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = User(username=request.form['username'], password=request.form['password'],
                    email=request.form['email'])
        db.session.add(user)
        db.session.commit()
        flash('Registered! Please login.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/submit', methods=['POST'])
@login_required
def submit_grant():
    name = request.form['grant_name']
    applicant = request.form['applicant']
    deadline = request.form.get('deadline')
    notes = request.form.get('notes')
    file = request.files.get('file')
    file_path = None
    if file:
        filename = secure_filename(file.filename)
        upload_folder = app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        file.save(os.path.join(upload_folder, filename))
        file_path = os.path.join('static', 'uploads', filename)
    grant = Grant(name=name, applicant=applicant, deadline=deadline, notes=notes, file_path=file_path, user_id=current_user.id)
    db.session.add(grant)
    db.session.commit()
    # Email notification
    if app.config.get('MAIL_USERNAME') and app.config.get('MAIL_PASSWORD'):
        msg = Message('New Grant Submission', sender=app.config['MAIL_USERNAME'], recipients=[current_user.email])
        msg.body = f"Grant '{name}' submitted by {applicant}."
        mail.send(msg)
    flash('Grant submitted!')
    return redirect(url_for('index'))

@app.route('/admin', methods=['GET'])
@login_required
def admin_panel():
    if not current_user.is_admin:
        return 'Unauthorized', 403
    grants = Grant.query.all()
    return render_template('admin.html', grants=grants)

@app.route('/update_status/<int:grant_id>', methods=['POST'])
@login_required
def update_status(grant_id):
    if not current_user.is_admin:
        return 'Unauthorized', 403
    status = request.form['status']
    grant = Grant.query.get(grant_id)
    grant.status = status
    db.session.commit()
    return redirect(url_for('admin_panel'))

@app.route('/export_csv')
@login_required
def export_csv():
    if not current_user.is_admin:
        return 'Unauthorized', 403
    grants = Grant.query.all()
    df = pd.DataFrame([{
        'Name': g.name, 'Applicant': g.applicant, 'Status': g.status,
        'Submitted': g.submitted_at, 'Deadline': g.deadline, 'Notes': g.notes
    } for g in grants])
    csv_path = 'instance/grants_export.csv'
    df.to_csv(csv_path, index=False)
    return send_file(csv_path, as_attachment=True)

# --- API for frontend filtering/search ---
@app.route('/api/grants')
@login_required
def api_grants():
    filter_status = request.args.get('status')
    query = Grant.query
    if filter_status:
        query = query.filter_by(status=filter_status)
    grants = query.all()
    return jsonify([{
        'id': g.id, 'name': g.name, 'applicant': g.applicant, 'status': g.status,
        'submitted_at': g.submitted_at, 'deadline': g.deadline, 'notes': g.notes
    } for g in grants])

# --- Dashboard Data for charts ---
@app.route('/api/dashboard')
@login_required
def api_dashboard():
    grants = Grant.query.all()
    status_counts = {}
    for g in grants:
        status_counts[g.status] = status_counts.get(g.status, 0) + 1
    return jsonify({'status_counts': status_counts})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)