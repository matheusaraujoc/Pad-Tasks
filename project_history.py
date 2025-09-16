# project_history.py
import json
import os
from datetime import datetime

# O nome do arquivo que guardará nosso histórico
HISTORY_FILE = 'projects.json'

def get_id_from_url(url):
    """Função de ajuda para extrair o ID da URL completa."""
    if not url:
        return None
    return url.strip().split('/')[-1]

def load_projects():
    """Lê os projetos do arquivo JSON e os retorna ordenados pelo mais recente."""
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Ordena a lista de projetos pela data de acesso, do mais novo para o mais antigo
            projects = data.get('projects', [])
            return sorted(projects, key=lambda p: p.get('last_accessed', ''), reverse=True)
    except (json.JSONDecodeError, IOError):
        return [] # Retorna lista vazia se o arquivo estiver corrompido ou ilegível

def save_projects(projects):
    """Salva a lista completa de projetos no arquivo JSON."""
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        # Usamos indent=4 para o arquivo ficar legível para humanos
        json.dump({'projects': projects}, f, indent=4)

def add_or_update_project(url, name):
    """
    Adiciona um novo projeto ao histórico (salvando apenas o ID) ou atualiza um existente.
    """
    project_id = get_id_from_url(url)
    if not project_id:
        return

    all_projects = load_projects()
    
    # Tenta encontrar se o projeto (pelo ID) já existe na lista
    project_found = next((p for p in all_projects if p.get('id') == project_id), None)

    if project_found:
        # Se encontrou, apenas atualiza a data de acesso e o nome (caso tenha mudado)
        project_found['last_accessed'] = datetime.now().isoformat()
        project_found['name'] = name
    else:
        # Se não encontrou, adiciona um novo dicionário à lista, usando 'id' em vez de 'url'
        all_projects.append({
            'name': name,
            'id': project_id,
            'last_accessed': datetime.now().isoformat()
        })
    
    # Salva a lista atualizada de volta no arquivo
    save_projects(all_projects)

def delete_project(url_to_delete):
    """
    Remove um projeto do histórico com base no ID extraído da sua URL.
    """
    project_id_to_delete = get_id_from_url(url_to_delete)
    if not project_id_to_delete:
        return

    # Carrega a lista de projetos existentes
    all_projects = load_projects()
    
    # Cria uma nova lista, mantendo apenas os projetos cujo ID NÃO é o que queremos deletar
    projects_to_keep = [p for p in all_projects if p.get('id') != project_id_to_delete]
    
    # Salva a nova lista (sem o projeto deletado) de volta no arquivo
    save_projects(projects_to_keep)

def get_project_name_by_id(project_id_to_find):
    """
    Busca no histórico de projetos e retorna o nome de um projeto com base no seu ID.
    """
    if not project_id_to_find:
        return None
    
    all_projects = load_projects()
    project_found = next((p for p in all_projects if p.get('id') == project_id_to_find), None)
    
    if project_found:
        return project_found.get('name')
    return None