import os
import json
import uuid
from flask import Flask, render_template, request, redirect, url_for, session
from git import Repo

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'chave_secreta_local_123')

ADMIN_USER = os.environ.get('ADMIN_PORT', os.environ.get('ADMIN_USER', 'admin'))
ADMIN_PASS = os.environ.get('SENHA_PORT', os.environ.get('ADMIN_PASS', 'admin123'))

DATA_FILE = 'data.json'
REPO_URL = 'https://github.com/matheus1996aleixo-wq/Matheus.Portifolio.git'

def init_git_repo():
    if not os.path.exists('.git'):
        repo = Repo.init(os.getcwd())
    else:
        repo = Repo(os.getcwd())
    
    if 'origin' in [r.name for r in repo.remotes]:
        origin = repo.remote(name='origin')
        origin.set_url(REPO_URL)
    else:
        repo.create_remote('origin', REPO_URL)

def load_data():
    if not os.path.exists(DATA_FILE):
        data = {"profile": {}, "skills": [], "projects": [], "formations": [], "experiences": []}
    else:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
    if 'skills' not in data: data['skills'] = []
    if 'experiences' not in data: data['experiences'] = []
    if 'projects' not in data: data['projects'] = []
    if 'formations' not in data: data['formations'] = []
    
    return data

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    try:
        init_git_repo()
        repo = Repo(os.getcwd())
        repo.git.add(DATA_FILE)
        repo.index.commit("Atualização automática via Painel Admin - Matheus.Portifolio")
        
        origin = repo.remote(name='origin')
        origin.push(refspec='main:main')
    except Exception as e:
        print(f"Erro ao subir para o GitHub: {e}")

@app.route('/')
def index():
    data = load_data()
    return render_template('index.html', data=data)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('logged_in'):
        return redirect(url_for('admin'))

    if request.method == 'POST':
        user = request.form.get('username')
        password = request.form.get('password')
        if user == ADMIN_USER and password == ADMIN_PASS:
            session['logged_in'] = True
            return redirect(url_for('admin'))
        else:
            return render_template('login.html', erro="Usuário ou senha incorretos.")
            
    return render_template('login.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    data = load_data()
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'update_profile':
            data['profile'] = {
                "full_name": request.form.get('full_name'),
                "date_of_birth": request.form.get('date_of_birth'),
                "city": request.form.get('city'),
                "state": request.form.get('state'),
                "country": request.form.get('country')
            }
        elif action == 'add_formation':
            new_formation = {
                "id": str(uuid.uuid4()),
                "level": request.form.get('level'),
                "course": request.form.get('course'),
                "entity_type": request.form.get('entity_type'),
                "entity_name": request.form.get('entity_name'),
                "completion_date": request.form.get('completion_date')
            }
            data['formations'].append(new_formation)
            
        elif action == 'delete_formation':
            form_id = request.form.get('form_id')
            data['formations'] = [f for f in data['formations'] if f.get('id') != form_id]

        elif action == 'add_project':
            new_project = {
                "id": str(uuid.uuid4()),
                "title": request.form.get('title'),
                "description": request.form.get('description'),
                "tech": request.form.get('tech'),
                "link_live": request.form.get('link_live'),
                "link_github": request.form.get('link_github')
            }
            data['projects'].append(new_project)
            
        elif action == 'delete_project':
            project_id = request.form.get('project_id')
            data['projects'] = [p for p in data['projects'] if p.get('id') != project_id]
            
        elif action == 'add_skill':
            new_skill = {
                "id": str(uuid.uuid4()),
                "category": request.form.get('category'),
                "name": request.form.get('name')
            }
            data['skills'].append(new_skill)
            
        elif action == 'delete_skill':
            skill_id = request.form.get('skill_id')
            data['skills'] = [s for s in data['skills'] if s.get('id') != skill_id]

        elif action == 'add_experience':
            new_experience = {
                "id": str(uuid.uuid4()),
                "title": request.form.get('title'),
                "description": request.form.get('description'),
                "period": request.form.get('period')
            }
            data['experiences'].append(new_experience)
            
        elif action == 'delete_experience':
            exp_id = request.form.get('exp_id')
            data['experiences'] = [e for e in data['experiences'] if e.get('id') != exp_id]
            
        save_data(data)
        return redirect(url_for('admin'))
        
    return render_template('admin.html', data=data)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_git_repo()
    app.run(debug=True, host='0.0.0.0', port=5000)