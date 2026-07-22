import os
import json
import uuid
from flask import Flask, render_template, request, redirect, url_for, session
from git import Repo

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'chave_secreta_local_123')

ADMIN_USER = os.environ.get('ADMIN_PORT', 'Matheus')
ADMIN_PASS = os.environ.get('SENHA_PORT', '@Kayle2023')

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
            
    if 'profile' not in data: data['profile'] = {}
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
        repo.index.commit("Atualização via Painel Admin - Matheus.Portifolio")
        
        origin = repo.remote(name='origin')
        origin.push(refspec='main:main')
    except Exception as e:
        print(f"Aviso Git: {e}")

@app.route('/lang/<lang_code>')
def set_language(lang_code):
    if lang_code in ['pt', 'en']:
        session['lang'] = lang_code
    return redirect(url_for('index'))

@app.route('/')
def index():
    data = load_data()
    lang = session.get('lang', 'pt')
    return render_template('index.html', data=data, lang=lang)

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
            erro_msg = "Usuário ou senha incorretos." if session.get('lang', 'pt') == 'pt' else "Incorrect username or password."
            return render_template('login.html', erro=erro_msg)
            
    return render_template('login.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    data = load_data()
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'update_profile':
            data['profile']['nome'] = request.form.get('nome')
            data['profile']['titulo_pt'] = request.form.get('titulo_pt')
            data['profile']['titulo_en'] = request.form.get('titulo_en')
            data['profile']['sobre_pt'] = request.form.get('sobre_pt')
            data['profile']['sobre_en'] = request.form.get('sobre_en')
            
            curriculo_file = request.files.get('curriculo_file')
            if curriculo_file and curriculo_file.filename:
                os.makedirs('static/uploads', exist_ok=True)
                path = os.path.join('static/uploads', curriculo_file.filename)
                curriculo_file.save(path)
                data['profile']['curriculo_file'] = '/' + path

            carta_file = request.files.get('carta_file')
            if carta_file and carta_file.filename:
                os.makedirs('static/uploads', exist_ok=True)
                path = os.path.join('static/uploads', carta_file.filename)
                carta_file.save(path)
                data['profile']['carta_file'] = '/' + path

        # FORMAÇÕES (Adicionar e Editar)
        elif action == 'add_formation':
            desc = request.form.get('description', '')
            new_formation = {
                "id": str(uuid.uuid4()),
                "level": request.form.get('level'),
                "course": request.form.get('course'),
                "entity_type": request.form.get('entity_type'),
                "entity_name": request.form.get('entity_name'),
                "completion_date": request.form.get('completion_date'),
                "description": desc
            }
            data['formations'].append(new_formation)
            
            for linha in desc.split('\n'):
                if ':' in linha:
                    partes = linha.split(':', 1)
                    cat = partes[0].strip()
                    det = partes[1].strip()
                    if not any(s['category'] == cat for s in data['skills']):
                        data['skills'].append({
                            "id": str(uuid.uuid4()),
                            "category": cat,
                            "name": cat,
                            "icon": "",
                            "detalhes": det
                        })
                        
        elif action == 'edit_formation':
            form_id = request.form.get('form_id')
            for f in data['formations']:
                if f.get('id') == form_id:
                    f['level'] = request.form.get('level')
                    f['course'] = request.form.get('course')
                    f['entity_type'] = request.form.get('entity_type')
                    f['entity_name'] = request.form.get('entity_name')
                    f['completion_date'] = request.form.get('completion_date')
                    f['description'] = request.form.get('description', '')

        elif action == 'delete_formation':
            form_id = request.form.get('form_id')
            data['formations'] = [f for f in data['formations'] if f.get('id') != form_id]

        # PROJETOS (Adicionar e Editar)
        elif action == 'add_project':
            new_project = {
                "id": str(uuid.uuid4()),
                "title": request.form.get('title'),
                "description": request.form.get('description'),
                "tech": request.form.get('tech'),
                "link_live": request.form.get('link_live', ''),
                "link_github": request.form.get('link_github', '')
            }
            data['projects'].append(new_project)
            
        elif action == 'edit_project':
            proj_id = request.form.get('project_id')
            for p in data['projects']:
                if p.get('id') == proj_id:
                    p['title'] = request.form.get('title')
                    p['description'] = request.form.get('description')
                    p['tech'] = request.form.get('tech')
                    p['link_live'] = request.form.get('link_live', '')
                    p['link_github'] = request.form.get('link_github', '')

        elif action == 'delete_project':
            project_id = request.form.get('project_id')
            data['projects'] = [p for p in data['projects'] if p.get('id') != project_id]
            
        # HABILIDADES (Adicionar e Editar)
        elif action == 'add_skill':
            new_skill = {
                "id": str(uuid.uuid4()),
                "category": request.form.get('category'),
                "name": request.form.get('name'),
                "icon": request.form.get('icon', ''),
                "detalhes": request.form.get('detalhes', '')
            }
            data['skills'].append(new_skill)
            
        elif action == 'edit_skill':
            skill_id = request.form.get('skill_id')
            for s in data['skills']:
                if s.get('id') == skill_id:
                    s['category'] = request.form.get('category')
                    s['name'] = request.form.get('name')
                    s['icon'] = request.form.get('icon', '')
                    s['detalhes'] = request.form.get('detalhes', '')

        elif action == 'delete_skill':
            skill_id = request.form.get('skill_id')
            data['skills'] = [s for s in data['skills'] if s.get('id') != skill_id]

        # EXPERIÊNCIAS (Adicionar e Editar)
        elif action == 'add_experience':
            new_experience = {
                "id": str(uuid.uuid4()),
                "title": request.form.get('title'),
                "description": request.form.get('description'),
                "period": request.form.get('period')
            }
            data['experiences'].append(new_experience)
            
        elif action == 'edit_experience':
            exp_id = request.form.get('exp_id')
            for e in data['experiences']:
                if e.get('id') == exp_id:
                    e['title'] = request.form.get('title')
                    e['description'] = request.form.get('description')
                    e['period'] = request.form.get('period')

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