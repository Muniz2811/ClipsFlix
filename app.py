from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
import cloudinary.api

load_dotenv()

# Configuração do banco de dados
if os.getenv('DATABASE_URL'):
    # Render PostgreSQL database
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL').replace('postgres://', 'postgresql://')
else:
    # SQLite local para desenvolvimento
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clips.db'

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback-secret-key')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Configuração do Cloudinary
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

# Modelos
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    clips = db.relationship('Clip', backref='author', lazy=True)

class Clip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    game = db.Column(db.String(100), nullable=False)
    video_url = db.Column(db.String(500), nullable=False)
    public_id = db.Column(db.String(200), nullable=False)
    upload_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Função para criar o banco de dados e o usuário admin
def init_db():
    with app.app_context():
        # Criar todas as tabelas
        db.create_all()
        
        # Verificar se já existe um usuário admin
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            # Criar usuário admin
            admin = User(
                username='admin',
                password_hash=generate_password_hash('admin123')
            )
            db.session.add(admin)
            db.session.commit()
            print('Usuário admin criado com sucesso!')

# Inicializar o banco de dados
init_db()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    clips = Clip.query.order_by(Clip.upload_date.desc()).all()
    print("Clips encontrados:", len(clips))
    for clip in clips:
        print(f"Clip ID: {clip.id}, Title: {clip.title}, URL: {clip.video_url}")
    return render_template('index.html', clips=clips)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('Nome de usuário já existe')
            return redirect(url_for('register'))
        
        user = User(username=username, password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('index'))
        flash('Usuário ou senha inválidos')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if 'video' not in request.files:
            print("Erro: Nenhum arquivo enviado")
            return jsonify({'success': False, 'message': 'Nenhum arquivo enviado'})
        
        file = request.files['video']
        if file.filename == '':
            print("Erro: Nenhum arquivo selecionado")
            return jsonify({'success': False, 'message': 'Nenhum arquivo selecionado'})
        
        try:
            print(f"Iniciando upload para Cloudinary: {file.filename}")
            # Upload para o Cloudinary
            result = cloudinary.uploader.upload(file,
                resource_type="video",
                folder="game_clips",
                eager=[{"streaming_profile": "full_hd"}],
                eager_async=True
            )
            print(f"Upload bem sucedido! URL: {result['secure_url']}")
            
            clip = Clip(
                title=request.form['title'],
                game=request.form['game'],
                video_url=result['secure_url'],
                public_id=result['public_id'],
                user_id=current_user.id
            )
            db.session.add(clip)
            db.session.commit()
            print(f"Clip salvo no banco de dados com ID: {clip.id}")
            
            return jsonify({'success': True, 'message': 'Upload realizado com sucesso'})
        except Exception as e:
            print(f"Erro durante o upload: {str(e)}")
            return jsonify({'success': False, 'message': f'Erro ao fazer upload: {str(e)}'})
            
    return render_template('upload.html')

@app.route('/delete/<int:clip_id>', methods=['POST'])
@login_required
def delete_clip(clip_id):
    clip = Clip.query.get_or_404(clip_id)
    if clip.user_id != current_user.id:
        flash('Você não tem permissão para deletar este clip')
        return redirect(url_for('index'))
    
    try:
        # Deletar do Cloudinary
        cloudinary.uploader.destroy(clip.public_id, resource_type="video")
        # Deletar do banco de dados
        db.session.delete(clip)
        db.session.commit()
        flash('Clip deletado com sucesso')
    except Exception as e:
        flash(f'Erro ao deletar clip: {str(e)}')
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
else:
    init_db()  # Isso garante que o banco seja criado no Render
