import os
import json
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'sua_chave_secreta_aqui'

UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

DATA_FILE = 'data.json'

def load_data():
    if not os.path.exists(DATA_FILE):
        default_data = {
            "profile": {},
            "formations": [],
            "skills": [],
            "experiences": [],
            "projects": []
        }
        save_data(default_data)
        return default_data
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Erro ao carregar {DATA_FILE}: {e}")
        return {"profile": {}, "formations": [], "skills": [], "experiences": [], "projects": []}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data.json')
def get_data():
    data = load_data()
    return jsonify(data)

@app.route('/login', methods=['GET', 'POST'])
def login():
    erro = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == 'admin' and password == '1234':
            session['logged_in'] = True
            return redirect(url_for('admin'))
        else:
            erro = "Usuário ou senha inválidos."
            
    return render_template('login.html', erro=erro)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    data = load_data()
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'update_profile':
            for key in request.form:
                if key != 'action':
                    data['profile'][key] = request.form[key]
            
            for file_key in ['foto_file', 'curriculo_file_pt', 'curriculo_file_en', 'carta_file_pt', 'carta_file_en']:
                if file_key in request.files:
                    file = request.files[file_key]
                    if file and file.filename != '':
                        filename = secure_filename(file.filename)
                        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                        file.save(filepath)
                        data['profile'][file_key.replace('_file', '')] = f'/static/uploads/{filename}'
            
            save_data(data)
            return redirect(url_for('admin') + '#tab-perfil')
            
        elif action in ['update_formations', 'add_formation', 'delete_formation']:
            if action == 'update_formations':
                for i, f in enumerate(data.get('formations', [])):
                    prefix = f"formation_{i}_"
                    if f"{prefix}course" in request.form:
                        f['course'] = request.form.get(f"{prefix}course", f.get('course'))
                        f['course_en'] = request.form.get(f"{prefix}course_en", f.get('course_en'))
                        f['entity_name'] = request.form.get(f"{prefix}entity_name", f.get('entity_name'))
                        f['entity_name_en'] = request.form.get(f"{prefix}entity_name_en", f.get('entity_name_en'))
                        f['completion_date'] = request.form.get(f"{prefix}completion_date", f.get('completion_date'))
                        f['description'] = request.form.get(f"{prefix}description", f.get('description'))
                        f['description_en'] = request.form.get(f"{prefix}description_en", f.get('description_en'))
            elif action == 'add_formation':
                new_id = str(len(data.get('formations', [])) + 1)
                new_item = {
                    "id": new_id,
                    "course": "Novo Curso",
                    "course_en": "New Course",
                    "entity_name": "Instituição",
                    "entity_name_en": "Institution",
                    "completion_date": "2026",
                    "description": "",
                    "description_en": "",
                    "entity_type": "Universidade",
                    "entity_type_en": "University",
                    "level": "Graduação",
                    "level_en": "Bachelor's"
                }
                data.setdefault('formations', []).append(new_item)
            elif action == 'delete_formation':
                idx = int(request.form.get('index', -1))
                if 0 <= idx < len(data.get('formations', [])):
                    data['formations'].pop(idx)
            save_data(data)
            return redirect(url_for('admin') + '#tab-formacoes')

        elif action in ['update_skills', 'add_skill', 'delete_skill']:
            if action == 'update_skills':
                for i, s in enumerate(data.get('skills', [])):
                    prefix = f"skill_{i}_"
                    if f"{prefix}category" in request.form:
                        s['category'] = request.form.get(f"{prefix}category", s.get('category'))
                        s['category_en'] = request.form.get(f"{prefix}category_en", s.get('category_en'))
                        s['detalhes'] = request.form.get(f"{prefix}detalhes", s.get('detalhes'))
                        s['detalhes_en'] = request.form.get(f"{prefix}detalhes_en", s.get('detalhes_en'))
            elif action == 'add_skill':
                new_id = str(len(data.get('skills', [])) + 1)
                new_item = {
                    "id": new_id,
                    "category": "Nova Habilidade",
                    "category_en": "New Skill",
                    "name": "Ferramenta",
                    "name_en": "Tool",
                    "detalhes": "",
                    "detalhes_en": "",
                    "icon": ""
                }
                data.setdefault('skills', []).append(new_item)
            elif action == 'delete_skill':
                idx = int(request.form.get('index', -1))
                if 0 <= idx < len(data.get('skills', [])):
                    data['skills'].pop(idx)
            save_data(data)
            return redirect(url_for('admin') + '#tab-habilidades')

        elif action in ['update_experiences', 'add_experience', 'delete_experience']:
            if action == 'update_experiences':
                for i, e in enumerate(data.get('experiences', [])):
                    prefix = f"exp_{i}_"
                    if f"{prefix}title" in request.form:
                        e['title'] = request.form.get(f"{prefix}title", e.get('title'))
                        e['title_en'] = request.form.get(f"{prefix}title_en", e.get('title_en'))
                        e['period'] = request.form.get(f"{prefix}period", e.get('period'))
                        e['period_en'] = request.form.get(f"{prefix}period_en", e.get('period_en'))
                        e['description'] = request.form.get(f"{prefix}description", e.get('description'))
                        e['description_en'] = request.form.get(f"{prefix}description_en", e.get('description_en'))
            elif action == 'add_experience':
                new_id = str(len(data.get('experiences', [])) + 1)
                new_item = {
                    "id": new_id,
                    "title": "Cargo - Empresa",
                    "title_en": "Position - Company",
                    "period": "2026 - Presente",
                    "period_en": "2026 - Present",
                    "description": "",
                    "description_en": ""
                }
                data.setdefault('experiences', []).append(new_item)
            elif action == 'delete_experience':
                idx = int(request.form.get('index', -1))
                if 0 <= idx < len(data.get('experiences', [])):
                    data['experiences'].pop(idx)
            save_data(data)
            return redirect(url_for('admin') + '#tab-experiencias')

        elif action in ['update_projects', 'add_project', 'delete_project']:
            if action == 'update_projects':
                for i, p in enumerate(data.get('projects', [])):
                    prefix = f"proj_{i}_"
                    if f"{prefix}title" in request.form:
                        p['title'] = request.form.get(f"{prefix}title", p.get('title'))
                        p['title_en'] = request.form.get(f"{prefix}title_en", p.get('title_en'))
                        p['description'] = request.form.get(f"{prefix}description", p.get('description'))
                        p['description_en'] = request.form.get(f"{prefix}description_en", p.get('description_en'))
                        p['tech'] = request.form.get(f"{prefix}tech", p.get('tech'))
            elif action == 'add_project':
                new_id = str(len(data.get('projects', [])) + 1)
                new_item = {
                    "id": new_id,
                    "title": "Novo Projeto",
                    "title_en": "New Project",
                    "description": "",
                    "description_en": "",
                    "tech": "Python, Flask",
                    "link_github": "",
                    "link_live": ""
                }
                data.setdefault('projects', []).append(new_item)
            elif action == 'delete_project':
                idx = int(request.form.get('index', -1))
                if 0 <= idx < len(data.get('projects', [])):
                    data['projects'].pop(idx)
            save_data(data)
            return redirect(url_for('admin') + '#tab-projetos')
            
        return redirect(url_for('admin'))
        
    return render_template('admin.html', data=data)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)