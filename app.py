import os
import json
import uuid
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from google import genai
from git import Repo

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'chave_secreta_local_123')
app.config['TEMPLATES_AUTO_RELOAD'] = True

ADMIN_USER = os.environ.get('ADMIN_PORT', 'admin')
ADMIN_PASS = os.environ.get('SENHA_PORT', 'admin123')

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
        data = {
            "profile": {},
            "skills": [],
            "projects": [],
            "formations": [],
            "experiences": []
        }
    else:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
    if 'profile' not in data: data['profile'] = {}
    if 'skills' not in data: data['skills'] = []
    if 'experiences' not in data: data['experiences'] = []
    if 'projects' not in data: data['projects'] = []
    if 'formations' not in data: data['formations'] = []
    
    novo_sobre_pt = (
        "Busco atuar como Analista de Sistemas ou Desenvolvedor, agregando valor estratégico por meio "
        "da criação de soluções tecnológicas eficientes e escaláveis. Meu objetivo é impulsionar a produtividade "
        "da organização atuando em três pilares principais:\n\n"
        "• Engenharia de Dados e Automação: Desenvolvimento de pipelines ETL escaláveis em nuvem, automação de "
        "processos com Python, integração de APIs e extração/tratamento avançado de dados estruturados (HTML, XML e JSON).\n\n"
        "• Sistemas e Infraestrutura: Construção e manutenção de aplicações, suporte técnico especializado, "
        "gestão de infraestrutura de TI e execução de testes funcionais para garantir a estabilidade e qualidade das operações.\n\n"
        "• Governança e Processos: Gestão eficiente de versionamento de código (Git/GitHub), aplicação de boas "
        "práticas de engenharia de software e visão analítica para garantir a segurança da informação e otimizar fluxos internos."
    )
    novo_sobre_en = (
        "Seeking to work as a Systems Analyst or Developer, adding strategic value through the creation of efficient and scalable technological solutions. My goal is to drive organizational productivity by acting across three main pillars:\n\n"
        "• Data Engineering & Automation: Development of scalable cloud ETL pipelines, Python process automation, API integration, and advanced extraction/treatment of structured data (HTML, XML, and JSON).\n\n"
        "• Systems & Infrastructure: Application construction and maintenance, specialized technical support, IT infrastructure management, and execution of functional tests to ensure operational stability and quality.\n\n"
        "• Governance & Processes: Efficient code versioning management (Git/GitHub), application of software engineering best practices, and analytical vision to ensure information security and optimize internal workflows."
    )
    
    if not data['profile'].get('sobre_pt'):
        data['profile']['sobre_pt'] = novo_sobre_pt
    data['profile']['sobre_en'] = novo_sobre_en

    default_comp_pt = (
        "Base sólida em algoritmos e programação, estruturas de dados, programação orientada a objetos (POO), "
        "modelagem e consultas em bancos de dados (SQL/MER/DER), desenvolvimento web e mobile, infraestrutura de servidores, "
        "inteligência artificial, segurança da informação, engenharia de software e execução de projetos integradores práticos."
    )
    default_comp_en = (
        "Solid foundation in algorithms and programming, data structures, object-oriented programming (OOP), "
        "database modeling and queries (SQL/ERD), web and mobile development, server infrastructure, "
        "artificial intelligence, information security, software engineering, and execution of practical integrative projects."
    )
    if not data['profile'].get('destaque_comp_pt'):
        data['profile']['destaque_comp_pt'] = default_comp_pt
    data['profile']['destaque_comp_en'] = default_comp_en

    default_titulo_pt = "Bacharelado em Tecnologia da Informação"
    default_titulo_en = "Bachelor's Degree in Information Technology"
    if not data['profile'].get('destaque_titulo_pt'):
        data['profile']['destaque_titulo_pt'] = default_titulo_pt
    data['profile']['destaque_titulo_en'] = default_titulo_en

    default_inst = "Universidade Virtual do Estado de São Paulo (UNIVESP)"
    default_inst_en = "Virtual University of the State of São Paulo (UNIVESP)"
    if not data['profile'].get('destaque_inst'):
        data['profile']['destaque_inst'] = default_inst
    data['profile']['destaque_inst_en'] = default_inst_en

    if not data['profile'].get('curriculo_titulo_pt'):
        data['profile']['curriculo_titulo_pt'] = "Download CV.Matheus : Portugues"
    if not data['profile'].get('curriculo_titulo_en'):
        data['profile']['curriculo_titulo_en'] = "Download CV.Matheus: Englês"
    if not data['profile'].get('carta_titulo_pt'):
        data['profile']['carta_titulo_pt'] = "Carta de Apresentação (PT)"
    if not data['profile'].get('carta_titulo_en'):
        data['profile']['carta_titulo_en'] = "Cover Letter (EN)"
        
    return data

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    try:
        init_git_repo()
        repo = Repo(os.getcwd())
        repo.git.add(all=True)
        repo.index.commit("Atualização automática via Painel Admin - Matheus.Portifolio")
        
        origin = repo.remote(name='origin')
        origin.push(refspec='main:main')
    except Exception as e:
        print(f"Aviso Git: {e}")

def translate_text(text, target_lang='en'):
    if not text:
        return text
    try:
        client = genai.Client()
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"Translate the following professional portfolio text into English. Keep formatting like [icon: ...] intact if present, and maintain a professional tone:\n\n{text}"
        )
        return response.text.strip()
    except Exception as e:
        print(f"Erro na tradução: {e}")
        return text

@app.route('/lang/<lang_code>')
def set_language(lang_code):
    if lang_code in ['pt', 'en']:
        session['lang'] = lang_code
    return redirect(url_for('index'))

@app.route('/')
def index():
    data = load_data()
    lang = session.get('lang', 'pt')
    
    translated_profile = data['profile'].copy()

    if lang == 'en':
        translated_profile['curriculo_file'] = data['profile'].get('curriculo_file_en', '')
        translated_profile['carta_file'] = data['profile'].get('carta_file_en', '')
        translated_profile['curriculo_titulo'] = data['profile'].get('curriculo_titulo_en', 'Download CV.Matheus: Englês')
        translated_profile['carta_titulo'] = data['profile'].get('carta_titulo_en', 'Cover Letter (EN)')
    else:
        translated_profile['curriculo_file'] = data['profile'].get('curriculo_file_pt', '')
        translated_profile['carta_file'] = data['profile'].get('carta_file_pt', '')
        translated_profile['curriculo_titulo'] = data['profile'].get('curriculo_titulo_pt', 'Download CV.Matheus : Portugues')
        translated_profile['carta_titulo'] = data['profile'].get('carta_titulo_pt', 'Carta de Apresentação (PT)')

    if lang == 'en':
        updated = False
        
        profile_fields_to_translate = [
            'titulo_pt', 'sobre_pt', 'idiomas_pt', 'disponibilidade_pt',
            'cidade', 'estado', 'pais', 'destaque_titulo_pt', 'destaque_comp_pt', 'destaque_inst',
            'curriculo_titulo_pt', 'carta_titulo_pt'
        ]
        for field in profile_fields_to_translate:
            if field in translated_profile and translated_profile[field]:
                en_field = field + '_en' if not field.endswith('_pt') else field.replace('_pt', '_en')
                if field in ['cidade', 'estado', 'pais', 'destaque_inst']:
                    en_field = field + '_en'
                
                if en_field in data['profile'] and data['profile'][en_field]:
                    translated_profile[field] = data['profile'][en_field]
                else:
                    tr = translate_text(str(translated_profile[field]))
                    data['profile'][en_field] = tr
                    translated_profile[field] = tr
                    updated = True

        translated_skills = []
        for s in data['skills']:
            ts = s.copy()
            for field in ['category', 'name', 'detalhes']:
                if field in ts and ts[field]:
                    en_field = field + '_en'
                    if en_field in ts and ts[en_field]:
                        ts[field] = ts[en_field]
                    else:
                        tr = translate_text(ts[field])
                        ts[en_field] = tr
                        s[en_field] = tr
                        ts[field] = tr
                        updated = True
            translated_skills.append(ts)
            
        translated_projects = []
        for p in data['projects']:
            tp = p.copy()
            for field in ['title', 'description', 'tech']:
                if field in tp and tp[field]:
                    en_field = field + '_en'
                    if en_field in tp and tp[en_field]:
                        tp[field] = tp[en_field]
                    else:
                        tr = translate_text(tp[field])
                        tp[en_field] = tr
                        p[en_field] = tr
                        tp[field] = tr
                        updated = True
            translated_projects.append(tp)
            
        translated_formations = []
        for f in data['formations']:
            tf = f.copy()
            for field in ['level', 'course', 'entity_type', 'entity_name', 'description', 'completion_date']:
                if field in tf and tf[field]:
                    en_field = field + '_en'
                    if en_field in tf and tf[en_field]:
                        tf[field] = tf[en_field]
                    else:
                        tr = translate_text(tf[field]) if field != 'completion_date' else tf[field]
                        tf[en_field] = tr
                        f[en_field] = tr
                        tf[field] = tr
                        updated = True
            translated_formations.append(tf)
            
        translated_experiences = []
        for e in data['experiences']:
            te = e.copy()
            for field in ['title', 'description', 'period']:
                if field in te and te[field]:
                    en_field = field + '_en'
                    if en_field in te and te[en_field]:
                        te[field] = te[en_field]
                    else:
                        tr = translate_text(te[field])
                        te[en_field] = tr
                        e[en_field] = tr
                        te[field] = tr
                        updated = True
            translated_experiences.append(te)
            
        if updated:
            save_data(data)

        translated_data = {
            "profile": translated_profile,
            "skills": translated_skills,
            "projects": translated_projects,
            "formations": translated_formations,
            "experiences": translated_experiences
        }
        
        return render_template('index.html', data=translated_data, lang=lang)
        
    translated_data = {
        "profile": translated_profile,
        "skills": data['skills'],
        "projects": data['projects'],
        "formations": data['formations'],
        "experiences": data['experiences']
    }
    return render_template('index.html', data=translated_data, lang=lang)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('logged_in'):
        return redirect(url_for('admin'))

    if request.method == 'POST':
        user = request.form.get('username')
        password = request.form.get('password')
        
        if ADMIN_USER and ADMIN_PASS and user == ADMIN_USER and password == ADMIN_PASS:
            session['logged_in'] = True
            return redirect(url_for('admin'))
        else:
            erro_msg = "Usuário ou senha incorretos." if session.get('lang', 'pt') == 'pt' else "Incorrect username or password."
            return render_template('login.html', erro=erro_msg)
            
    return render_template('login.html')

# NOVA ROTA: Tradução Automática na Tela do Admin
@app.route('/api/translate', methods=['POST'])
def api_translate():
    if not session.get('logged_in'):
        return jsonify({"translated": ""})
    data = request.get_json()
    text = data.get('text', '') if data else ''
    if not text:
        return jsonify({"translated": ""})
    return jsonify({"translated": translate_text(text)})

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    data = load_data()
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'update_profile':
            if 'nome' in request.form: data['profile']['nome'] = request.form.get('nome')
            if 'foto_url' in request.form: data['profile']['foto'] = request.form.get('foto_url')
            if 'nascimento' in request.form: data['profile']['nascimento'] = request.form.get('nascimento')
            
            if 'cidade' in request.form: 
                val = request.form.get('cidade')
                val_en = request.form.get('cidade_en')
                data['profile']['cidade'] = val
                data['profile']['cidade_en'] = val_en if val_en else translate_text(val)
            if 'estado' in request.form: 
                val = request.form.get('estado')
                val_en = request.form.get('estado_en')
                data['profile']['estado'] = val
                data['profile']['estado_en'] = val_en if val_en else translate_text(val)
            if 'pais' in request.form: 
                val = request.form.get('pais')
                val_en = request.form.get('pais_en')
                data['profile']['pais'] = val
                data['profile']['pais_en'] = val_en if val_en else translate_text(val)
                
            if 'linkedin' in request.form: data['profile']['linkedin'] = request.form.get('linkedin')
            if 'github' in request.form: data['profile']['github'] = request.form.get('github')

            if 'titulo_pt' in request.form:
                val_pt = request.form.get('titulo_pt')
                val_en = request.form.get('titulo_en')
                data['profile']['titulo_pt'] = val_pt
                data['profile']['titulo_en'] = val_en if val_en else translate_text(val_pt)
                
            if 'sobre_pt' in request.form:
                val_pt = request.form.get('sobre_pt')
                val_en = request.form.get('sobre_en')
                data['profile']['sobre_pt'] = val_pt
                data['profile']['sobre_en'] = val_en if val_en else translate_text(val_pt)
            
            if 'idiomas_pt' in request.form:
                val_pt = request.form.get('idiomas_pt')
                val_en = request.form.get('idiomas_en')
                data['profile']['idiomas_pt'] = val_pt
                data['profile']['idiomas_en'] = val_en if val_en else translate_text(val_pt)
                
            if 'disponibilidade_pt' in request.form:
                val_pt = request.form.get('disponibilidade_pt')
                val_en = request.form.get('disponibilidade_en')
                data['profile']['disponibilidade_pt'] = val_pt
                data['profile']['disponibilidade_en'] = val_en if val_en else translate_text(val_pt)

            if 'destaque_titulo_pt' in request.form:
                data['profile']['destaque_data'] = request.form.get('destaque_data')
                val_data_en = request.form.get('destaque_data_en')
                data['profile']['destaque_data_en'] = val_data_en if val_data_en else request.form.get('destaque_data')
                
                val_inst = request.form.get('destaque_inst')
                val_inst_en = request.form.get('destaque_inst_en')
                data['profile']['destaque_inst'] = val_inst
                data['profile']['destaque_inst_en'] = val_inst_en if val_inst_en else translate_text(val_inst)
                
                val_tit_pt = request.form.get('destaque_titulo_pt')
                val_tit_en = request.form.get('destaque_titulo_en')
                data['profile']['destaque_titulo_pt'] = val_tit_pt
                data['profile']['destaque_titulo_en'] = val_tit_en if val_tit_en else translate_text(val_tit_pt)
                
                val_comp_pt = request.form.get('destaque_comp_pt')
                val_comp_en = request.form.get('destaque_comp_en')
                data['profile']['destaque_comp_pt'] = val_comp_pt
                data['profile']['destaque_comp_en'] = val_comp_en if val_comp_en else translate_text(val_comp_pt)

            if 'curriculo_titulo_pt' in request.form:
                val_pt = request.form.get('curriculo_titulo_pt')
                val_en = request.form.get('curriculo_titulo_en')
                data['profile']['curriculo_titulo_pt'] = val_pt
                data['profile']['curriculo_titulo_en'] = val_en if val_en else translate_text(val_pt)

            if 'carta_titulo_pt' in request.form:
                val_pt = request.form.get('carta_titulo_pt')
                val_en = request.form.get('carta_titulo_en')
                data['profile']['carta_titulo_pt'] = val_pt
                data['profile']['carta_titulo_en'] = val_en if val_en else translate_text(val_pt)

            curriculo_file_pt = request.files.get('curriculo_file_pt')
            if curriculo_file_pt and curriculo_file_pt.filename:
                os.makedirs('static/uploads', exist_ok=True)
                path = os.path.join('static/uploads', curriculo_file_pt.filename)
                curriculo_file_pt.save(path)
                data['profile']['curriculo_file_pt'] = '/' + path

            curriculo_file_en = request.files.get('curriculo_file_en')
            if curriculo_file_en and curriculo_file_en.filename:
                os.makedirs('static/uploads', exist_ok=True)
                path = os.path.join('static/uploads', curriculo_file_en.filename)
                curriculo_file_en.save(path)
                data['profile']['curriculo_file_en'] = '/' + path

            carta_file_pt = request.files.get('carta_file_pt')
            if carta_file_pt and carta_file_pt.filename:
                os.makedirs('static/uploads', exist_ok=True)
                path = os.path.join('static/uploads', carta_file_pt.filename)
                carta_file_pt.save(path)
                data['profile']['carta_file_pt'] = '/' + path

            carta_file_en = request.files.get('carta_file_en')
            if carta_file_en and carta_file_en.filename:
                os.makedirs('static/uploads', exist_ok=True)
                path = os.path.join('static/uploads', carta_file_en.filename)
                carta_file_en.save(path)
                data['profile']['carta_file_en'] = '/' + path
                
            foto_file = request.files.get('foto_file')
            if foto_file and foto_file.filename:
                os.makedirs('static/uploads', exist_ok=True)
                path = os.path.join('static/uploads', foto_file.filename)
                foto_file.save(path)
                data['profile']['foto'] = '/' + path

        elif action == 'add_formation':
            desc = request.form.get('description', '')
            desc_en = request.form.get('description_en', '')
            level = request.form.get('level')
            level_en = request.form.get('level_en')
            course = request.form.get('course')
            course_en = request.form.get('course_en')
            ent_type = request.form.get('entity_type')
            ent_type_en = request.form.get('entity_type_en')
            ent_name = request.form.get('entity_name')
            ent_name_en = request.form.get('entity_name_en')
            comp_date = request.form.get('completion_date')
            comp_date_en = request.form.get('completion_date_en')

            new_formation = {
                "id": str(uuid.uuid4()),
                "level": level,
                "level_en": level_en if level_en else translate_text(level),
                "course": course,
                "course_en": course_en if course_en else translate_text(course),
                "entity_type": ent_type,
                "entity_type_en": ent_type_en if ent_type_en else translate_text(ent_type),
                "entity_name": ent_name,
                "entity_name_en": ent_name_en if ent_name_en else translate_text(ent_name),
                "completion_date": comp_date,
                "completion_date_en": comp_date_en if comp_date_en else comp_date,
                "description": desc,
                "description_en": desc_en if desc_en else translate_text(desc)
            }
            data['formations'].append(new_formation)
            
        elif action == 'edit_formation':
            form_id = request.form.get('form_id')
            for f in data['formations']:
                if f.get('id') == form_id:
                    f['level'] = request.form.get('level')
                    level_en = request.form.get('level_en')
                    f['level_en'] = level_en if level_en else translate_text(f['level'])
                    
                    f['course'] = request.form.get('course')
                    course_en = request.form.get('course_en')
                    f['course_en'] = course_en if course_en else translate_text(f['course'])
                    
                    f['entity_type'] = request.form.get('entity_type')
                    ent_type_en = request.form.get('entity_type_en')
                    f['entity_type_en'] = ent_type_en if ent_type_en else translate_text(f['entity_type'])
                    
                    f['entity_name'] = request.form.get('entity_name')
                    ent_name_en = request.form.get('entity_name_en')
                    f['entity_name_en'] = ent_name_en if ent_name_en else translate_text(f['entity_name'])
                    
                    f['completion_date'] = request.form.get('completion_date')
                    comp_date_en = request.form.get('completion_date_en')
                    f['completion_date_en'] = comp_date_en if comp_date_en else f['completion_date']
                    
                    desc = request.form.get('description', '')
                    desc_en = request.form.get('description_en', '')
                    f['description'] = desc
                    f['description_en'] = desc_en if desc_en else translate_text(desc)

        elif action == 'delete_formation':
            form_id = request.form.get('form_id')
            data['formations'] = [f for f in data['formations'] if f.get('id') != form_id]

        elif action == 'update_formation_module_icon':
            form_id = request.form.get('form_id')
            target_materia = request.form.get('materia_nome')
            new_icon = request.form.get('icon_url', '')
            
            sub_file = request.files.get('icon_file')
            if sub_file and sub_file.filename:
                os.makedirs('static/uploads', exist_ok=True)
                path = os.path.join('static/uploads', sub_file.filename)
                sub_file.save(path)
                new_icon = '/' + path

            for f in data['formations']:
                if f.get('id') == form_id:
                    linhas = f['description'].split('\n')
                    novas_linhas = []
                    for linha in linhas:
                        if ':' in linha:
                            partes = linha.split(':', 1)
                            mat = partes[0].strip()
                            if mat == target_materia:
                                resto = partes[1].strip()
                                if '[icon:' in resto:
                                    resto = resto.split('[icon:')[0].strip()
                                if new_icon:
                                    nova_linha = f"{mat}: {resto} [icon: {new_icon}]"
                                else:
                                    nova_linha = f"{mat}: {resto}"
                                novas_linhas.append(nova_linha)
                            else:
                                novas_linhas.append(linha)
                        else:
                            novas_linhas.append(linha)
                    f['description'] = '\n'.join(novas_linhas)
                    f['description_en'] = translate_text(f['description'])

        elif action == 'delete_formation_module':
            form_id = request.form.get('form_id')
            target_materia = request.form.get('materia_nome')
            for f in data['formations']:
                if f.get('id') == form_id:
                    linhas = f['description'].split('\n')
                    novas_linhas = [l for l in linhas if not (':' in l and l.split(':', 1)[0].strip() == target_materia)]
                    f['description'] = '\n'.join(novas_linhas)
                    f['description_en'] = translate_text(f['description'])

        elif action == 'add_project':
            desc = request.form.get('description', '')
            desc_en = request.form.get('description_en', '')
            tech = request.form.get('tech', '')
            tech_en = request.form.get('tech_en', '')
            title = request.form.get('title', '')
            title_en = request.form.get('title_en', '')
            
            new_project = {
                "id": str(uuid.uuid4()),
                "title": title,
                "title_en": title_en if title_en else translate_text(title),
                "description": desc,
                "description_en": desc_en if desc_en else translate_text(desc),
                "tech": tech,
                "tech_en": tech_en if tech_en else translate_text(tech),
                "link_live": request.form.get('link_live', ''),
                "link_github": request.form.get('link_github', '')
            }
            data['projects'].append(new_project)
            
        elif action == 'edit_project':
            proj_id = request.form.get('project_id')
            for p in data['projects']:
                if p.get('id') == proj_id:
                    title = request.form.get('title', '')
                    title_en = request.form.get('title_en', '')
                    desc = request.form.get('description', '')
                    desc_en = request.form.get('description_en', '')
                    tech = request.form.get('tech', '')
                    tech_en = request.form.get('tech_en', '')
                    
                    p['title'] = title
                    p['title_en'] = title_en if title_en else translate_text(title)
                    p['description'] = desc
                    p['description_en'] = desc_en if desc_en else translate_text(desc)
                    p['tech'] = tech
                    p['tech_en'] = tech_en if tech_en else translate_text(tech)
                    p['link_live'] = request.form.get('link_live', '')
                    p['link_github'] = request.form.get('link_github', '')

        elif action == 'delete_project':
            project_id = request.form.get('project_id')
            data['projects'] = [p for p in data['projects'] if p.get('id') != project_id]
            
        elif action == 'add_skill':
            icon_url = request.form.get('icon', '')
            skill_image = request.files.get('skill_image')
            if skill_image and skill_image.filename:
                os.makedirs('static/uploads', exist_ok=True)
                path = os.path.join('static/uploads', skill_image.filename)
                skill_image.save(path)
                icon_url = '/' + path

            cat = request.form.get('category', '')
            cat_en = request.form.get('category_en', '')
            name = request.form.get('name', '')
            name_en = request.form.get('name_en', '')
            det = request.form.get('detalhes', '')
            det_en = request.form.get('detalhes_en', '')
            
            new_skill = {
                "id": str(uuid.uuid4()),
                "category": cat,
                "category_en": cat_en if cat_en else translate_text(cat),
                "name": name,
                "name_en": name_en if name_en else translate_text(name),
                "icon": icon_url,
                "detalhes": det,
                "detalhes_en": det_en if det_en else translate_text(det)
            }
            data['skills'].append(new_skill)
            
        elif action == 'edit_skill':
            skill_id = request.form.get('skill_id')
            for s in data['skills']:
                if s.get('id') == skill_id:
                    cat = request.form.get('category', '')
                    cat_en = request.form.get('category_en', '')
                    name = request.form.get('name', '')
                    name_en = request.form.get('name_en', '')
                    det = request.form.get('detalhes', '')
                    det_en = request.form.get('detalhes_en', '')
                    
                    s['category'] = cat
                    s['category_en'] = cat_en if cat_en else translate_text(cat)
                    s['name'] = name
                    s['name_en'] = name_en if name_en else translate_text(name)
                    s['detalhes'] = det
                    s['detalhes_en'] = det_en if det_en else translate_text(det)
                    
                    icon_url = request.form.get('icon', '')
                    skill_image = request.files.get('skill_image')
                    if skill_image and skill_image.filename:
                        os.makedirs('static/uploads', exist_ok=True)
                        path = os.path.join('static/uploads', skill_image.filename)
                        skill_image.save(path)
                        icon_url = '/' + path
                    if icon_url:
                        s['icon'] = icon_url

        elif action == 'delete_skill':
            skill_id = request.form.get('skill_id')
            data['skills'] = [s for s in data['skills'] if s.get('id') != skill_id]

        elif action == 'add_experience':
            title = request.form.get('title', '')
            title_en = request.form.get('title_en', '')
            desc = request.form.get('description', '')
            desc_en = request.form.get('description_en', '')
            period = request.form.get('period', '')
            period_en = request.form.get('period_en', '')
            
            new_experience = {
                "id": str(uuid.uuid4()),
                "title": title,
                "title_en": title_en if title_en else translate_text(title),
                "description": desc,
                "description_en": desc_en if desc_en else translate_text(desc),
                "period": period,
                "period_en": period_en if period_en else translate_text(period)
            }
            data['experiences'].append(new_experience)
            
        elif action == 'edit_experience':
            exp_id = request.form.get('exp_id')
            for e in data['experiences']:
                if e.get('id') == exp_id:
                    title = request.form.get('title', '')
                    title_en = request.form.get('title_en', '')
                    desc = request.form.get('description', '')
                    desc_en = request.form.get('description_en', '')
                    period = request.form.get('period', '')
                    period_en = request.form.get('period_en', '')
                    
                    e['title'] = title
                    e['title_en'] = title_en if title_en else translate_text(title)
                    e['description'] = desc
                    e['description_en'] = desc_en if desc_en else translate_text(desc)
                    e['period'] = period
                    e['period_en'] = period_en if period_en else translate_text(period)

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
    app.run(debug=False, host='0.0.0.0', port=5000)