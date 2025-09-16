# project_history.py (VERSÃO CORRIGIDA)
import json
import os
from datetime import datetime

HISTORY_FILE = 'projects.json'

def load_projects():
    """Lê os projetos do arquivo JSON e os retorna ordenados pelo mais recente."""
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            projects = data.get('projects', [])
            return sorted(projects, key=lambda p: p.get('last_accessed', ''), reverse=True)
    except (json.JSONDecodeError, IOError):
        return []

def save_projects(projects):
    """Salva a lista completa de projetos no arquivo JSON."""
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump({'projects': projects}, f, indent=4)

def add_or_update_project(url, name):
    """
    Adiciona um novo projeto (usando a URL completa como ID) ou atualiza um existente.
    """
    if not url:
        return

    all_projects = load_projects()
    
    # ALTERADO: A URL completa agora é o identificador único
    project_found = next((p for p in all_projects if p.get('url') == url), None)

    if project_found:
        project_found['last_accessed'] = datetime.now().isoformat()
        project_found['name'] = name
    else:
        # ALTERADO: Salva o dicionário com a 'url' completa
        all_projects.append({
            'name': name,
            'url': url,
            'last_accessed': datetime.now().isoformat()
        })
    
    save_projects(all_projects)

def delete_project(url_to_delete):
    """
    Remove um projeto do histórico com base na sua URL completa.
    """
    if not url_to_delete:
        return

    all_projects = load_projects()
    
    # ALTERADO: Filtra pela URL completa
    projects_to_keep = [p for p in all_projects if p.get('url') != url_to_delete]
    
    save_projects(projects_to_keep)

def get_project_name_by_url(url_to_find):
    """
    Busca e retorna o nome de um projeto com base na sua URL completa.
    """
    if not url_to_find:
        return None
    
    all_projects = load_projects()
    project_found = next((p for p in all_projects if p.get('url') == url_to_find), None)
    
    if project_found:
        return project_found.get('name')
    return None