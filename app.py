import os
import json
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'

DATA_FILE = 'data.json'

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"profile": {}, "formations": [], "skills": [], "experiences": [], "projects": []}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/data.json')
def get_data_json():
    return send_from_directory('.', 'data.json')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == 'admin123':
            session['logged_in'] = True
            return redirect(url_for('admin'))
        return render_template('login.html', error='Senha incorreta')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    data = load_data()

    if request.method == 'POST':
        action = request.form.get('action')
        
        # 1. Atualizar Perfil e Destaque
        if action == 'update_profile':
            data['profile']['nome'] = request.form.get('nome', '')
            data['profile']['nascimento'] = request.form.get('nascimento', '')
            data['profile']['cidade'] = request.form.get('cidade', '')
            data['profile']['estado'] = request.form.get('estado', '')
            data['profile']['pais'] = request.form.get('pais', '')
            data['profile']['titulo_pt'] = request.form.get('titulo_pt', '')
            data['profile']['titulo_en'] = request.form.get('titulo_en', '')
            data['profile']['sobre_pt'] = request.form.get('sobre_pt', '')
            data['profile']['sobre_en'] = request.form.get('sobre_en', '')
            data['profile']['destaque_data'] = request.form.get('destaque_data', '')
            data['profile']['destaque_titulo_pt'] = request.form.get('destaque_titulo_pt', '')
            data['profile']['destaque_titulo_en'] = request.form.get('destaque_titulo_en', '')
            data['profile']['destaque_inst'] = request.form.get('destaque_inst', '')
            data['profile']['destaque_inst_en'] = request.form.get('destaque_inst_en', '')
            data['profile']['destaque_comp_pt'] = request.form.get('destaque_comp_pt', '')
            data['profile']['destaque_comp_en'] = request.form.get('destaque_comp_en', '')
            data['profile']['idiomas_pt'] = request.form.get('idiomas_pt', '')
            data['profile']['idiomas_en'] = request.form.get('idiomas_en', '')
            data['profile']['disponibilidade_pt'] = request.form.get('disponibilidade_pt', '')
            data['profile']['disponibilidade_en'] = request.form.get('disponibilidade_en', '')
            data['profile']['linkedin'] = request.form.get('linkedin', '')
            data['profile']['github'] = request.form.get('github', '')
        
        # 2. Atualizar Formações
        elif action == 'update_formations':
            for i, f in enumerate(data.get('formations', [])):
                f['entity_type'] = request.form.get(f'formation_{i}_entity_type', 'Universidade')
                f['completion_date'] = request.form.get(f'formation_{i}_completion_date', '')
                f['course'] = request.form.get(f'formation_{i}_course', '')
                f['course_en'] = request.form.get(f'formation_{i}_course_en', '')
                f['entity_name'] = request.form.get(f'formation_{i}_entity_name', '')
                f['entity_name_en'] = request.form.get(f'formation_{i}_entity_name_en', '')
                f['description'] = request.form.get(f'formation_{i}_description', '')
                f['description_en'] = request.form.get(f'formation_{i}_description_en', '')
        
        elif action == 'add_formation':
            if 'formations' not in data:
                data['formations'] = []
            data['formations'].append({
                "id": int(os.urandom(4).hex(), 16),
                "entity_type": "Universidade",
                "completion_date": "2026",
                "course": "Novo Curso",
                "course_en": "New Course",
                "entity_name": "Instituição",
                "entity_name_en": "Institution",
                "description": "",
                "description_en": ""
            })
        
        elif action == 'delete_formation':
            idx = request.form.get('index')
            if idx is not None and idx.isdigit():
                idx = int(idx)
                if 'formations' in data and 0 <= idx < len(data['formations']):
                    data['formations'].pop(idx)

        # 3. Atualizar Habilidades
        elif action == 'update_skills':
            for i, s in enumerate(data.get('skills', [])):
                s['category'] = request.form.get(f'skill_{i}_category', '')
                s['category_en'] = request.form.get(f'skill_{i}_category_en', '')
                s['detalhes'] = request.form.get(f'skill_{i}_detalhes', '')
                s['detalhes_en'] = request.form.get(f'skill_{i}_detalhes_en', '')

        elif action == 'add_skill':
            if 'skills' not in data:
                data['skills'] = []
            data['skills'].append({
                "id": int(os.urandom(4).hex(), 16),
                "category": "Nova Habilidade",
                "category_en": "New Skill",
                "detalhes": "",
                "detalhes_en": ""
            })

        elif action == 'delete_skill':
            idx = request.form.get('index')
            if idx is not None and idx.isdigit():
                idx = int(idx)
                if 'skills' in data and 0 <= idx < len(data['skills']):
                    data['skills'].pop(idx)

        # 4. Atualizar Experiências
        elif action == 'update_experiences':
            for i, e in enumerate(data.get('experiences', [])):
                e['title'] = request.form.get(f'exp_{i}_title', '')
                e['title_en'] = request.form.get(f'exp_{i}_title_en', '')
                e['period'] = request.form.get(f'exp_{i}_period', '')
                e['period_en'] = request.form.get(f'exp_{i}_period_en', '')
                e['description'] = request.form.get(f'exp_{i}_description', '')
                e['description_en'] = request.form.get(f'exp_{i}_description_en', '')

        elif action == 'add_experience':
            if 'experiences' not in data:
                data['experiences'] = []
            data['experiences'].append({
                "id": int(os.urandom(4).hex(), 16),
                "title": "Novo Cargo - Empresa",
                "title_en": "New Role - Company",
                "period": "2026",
                "period_en": "2026",
                "description": "",
                "description_en": ""
            })

        elif action == 'delete_experience':
            idx = request.form.get('index')
            if idx is not None and idx.isdigit():
                idx = int(idx)
                if 'experiences' in data and 0 <= idx < len(data['experiences']):
                    data['experiences'].pop(idx)

        # 5. Atualizar Projetos
        elif action == 'update_projects':
            for i, p in enumerate(data.get('projects', [])):
                p['title'] = request.form.get(f'proj_{i}_title', '')
                p['title_en'] = request.form.get(f'proj_{i}_title_en', '')
                p['description'] = request.form.get(f'proj_{i}_description', '')
                p['description_en'] = request.form.get(f'proj_{i}_description_en', '')
                p['tech'] = request.form.get(f'proj_{i}_tech', '')

        elif action == 'add_project':
            if 'projects' not in data:
                data['projects'] = []
            data['projects'].append({
                "id": int(os.urandom(4).hex(), 16),
                "title": "Novo Projeto",
                "title_en": "New Project",
                "description": "",
                "description_en": "",
                "tech": "Python, Flask"
            })

        elif action == 'delete_project':
            idx = request.form.get('index')
            if idx is not None and idx.isdigit():
                idx = int(idx)
                if 'projects' in data and 0 <= idx < len(data['projects']):
                    data['projects'].pop(idx)

        save_data(data)
        return redirect(url_for('admin'))

    return render_template('admin.html', data=data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)