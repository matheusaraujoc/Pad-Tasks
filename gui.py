# gui.py
import sys
import json
import uuid
import base64
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QTableWidget, QTableWidgetItem, QPushButton,
    QDialog, QFormLayout, QTextEdit, QComboBox, QDialogButtonBox,
    QMessageBox, QHeaderView, QFileDialog, QToolTip, QLineEdit,
    QInputDialog, QLabel, QListWidget, QListWidgetItem, QFrame,
    QRadioButton
)
from PySide6.QtGui import QColor, QAction, QFont
from PySide6.QtCore import Qt, QTimer, QThread, QObject, Signal, QSize

from etherpad_manager import SeleniumManager, Worker
import project_history

# --- Estilo Visual (QSS) - Tema "Modern Slate" ---
STYLE_SHEET = """
    /* Fundo principal e fonte */
    QWidget {
        background-color: #282c34;
        color: #abb2bf;
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 10pt;
    }
    
    /* Abas */
    QTabWidget::pane {
        border: none;
        border-top: 2px solid #3e4451;
    }
    QTabBar::tab {
        background: #282c34;
        color: #7f848e;
        padding: 10px 25px;
        border: none;
        border-top-left-radius: 5px;
        border-top-right-radius: 5px;
        font-weight: bold;
    }
    QTabBar::tab:hover {
        color: #abb2bf;
    }
    QTabBar::tab:selected {
        background: #3e4451;
        color: #ffffff;
        border-top: 2px solid #61afef;
    }

    /* Tabela */
    QTableWidget {
        background-color: #2c313a;
        border: none;
        gridline-color: #3e4451;
    }
    QHeaderView::section {
        background-color: #282c34;
        padding: 10px;
        border: none;
        border-bottom: 2px solid #3e4451;
        font-weight: bold;
        color: #ffffff;
    }
    QTableWidget::item {
        padding: 10px;
        border-bottom: 1px solid #3e4451;
    }
    QTableWidget::item:selected {
        background-color: rgba(97, 175, 239, 0.3);
        color: #ffffff;
    }

    /* Barra de Rolagem */
    QScrollBar:vertical {
        border: none;
        background-color: #2c313a; /* Cor de fundo da tabela */
        width: 14px;
        margin: 0px;
    }
    QScrollBar::handle:vertical {
        background-color: #4b5263; /* Cor dos botões */
        min-height: 25px;
        border-radius: 6px;
    }
    QScrollBar::handle:vertical:hover {
        background-color: #565f72; /* Cor de hover dos botões */
    }
    /* Esconde as setas da barra de rolagem para um look mais moderno */
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
        border: none;
        background: none;
    }
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
        background: none;
    }

    /* Estilo para a barra de rolagem horizontal, para consistência */
    QScrollBar:horizontal {
        border: none;
        background-color: #2c313a;
        height: 14px;
        margin: 0px;
    }
    QScrollBar::handle:horizontal {
        background-color: #4b5263;
        min-width: 25px;
        border-radius: 6px;
    }
    QScrollBar::handle:horizontal:hover {
        background-color: #565f72;
    }
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        width: 0px;
        border: none;
        background: none;
    }
    QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
        background: none;
    }

    /* Botões (Genérico) */
    QPushButton {
        background-color: #4b5263;
        color: #ffffff;
        border: none;
        padding: 9px 20px;
        border-radius: 5px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #565f72;
    }
    QPushButton:pressed {
        background-color: #3e4451;
    }

    /* Inputs */
    QLineEdit, QTextEdit, QComboBox {
        background-color: #21252b;
        border: 1px solid #3e4451;
        border-radius: 4px;
        padding: 5px;
        color: #dcdcdc;
    }
    
    /* Menus */
    QMenuBar { background-color: #21252b; }
    QMenuBar::item:selected { background-color: #3e4451; }
    QMenu { background-color: #2c313a; border: 1px solid #4b5263; }
    QMenu::item:selected { background-color: #61afef; color: #21252b; }

    /* === ESTILOS DA NOVA TELA DE PROJETOS === */
    #WelcomeDialog {
        background-color: #21252b;
    }
    
    #Sidebar {
        background-color: #282c34;
        border-right: 1px solid #3e4451;
    }
    
    #SidebarButton {
        background-color: #2c313a;
        text-align: left;
        padding: 15px;
        font-size: 11pt;
    }
    #SidebarButton:hover {
        background-color: #3e4451;
    }
    
    #WelcomeTitle {
        font-size: 18pt;
        font-weight: bold;
        color: #ffffff;
        padding-bottom: 10px;
    }
    
    QListWidget#ProjectList {
        background-color: transparent;
        border: none;
        outline: 0;
    }

    /* O próprio ITEM da lista agora é o nosso card. */
    QListWidget#ProjectList::item {
        background-color: #2c313a;
        border: 1px solid #4b5263;
        border-radius: 5px;
        color: #abb2bf;
        padding: 0px; 
    }

    QListWidget#ProjectList::item:hover {
        background-color: #3e4451;
        border: none;
    }
    
    QListWidget#ProjectList::item:selected {
        background-color: #3e4451; 
    }

    #ProjectCard {
        background-color: transparent;
        border: none;
        padding: 0;
    }
    
    #ProjectNameLabel {
        font-size: 12pt;
        font-weight: bold;
        color: #dcdcdc;
        background-color: transparent;
        border: none;
    }
    
    #ProjectUrlLabel, #ProjectDateLabel {
        font-size: 9pt;
        color: #7f848e;
        background-color: transparent;
    }
    
    QPushButton#CardButton {
        background-color: #4b5263;
        color: #ffffff;
        border: none;
        border-radius: 5px;
        font-weight: bold;
        font-size: 9pt;
        padding: 8px 15px;
    }
    QPushButton#CardButton:hover {
        background-color: #565f72;
    }

    QPushButton#PrimaryCardButton {
        border: none;
        border-radius: 5px;
        font-weight: bold;
        font-size: 9pt;
        padding: 8px 15px;
        background-color: #61afef;
        color: #21252b;
    }
    QPushButton#PrimaryCardButton:hover {
        background-color: #82c0f2;
    }

     /* Botão de Excluir (vermelho) */
    QPushButton#DeleteButton {
        background-color: #E06C75; /* Vermelho do tema */
        color: #282c34;
    }
    QPushButton#DeleteButton:hover {
        background-color: #c45a61; /* Vermelho um pouco mais escuro */
    }
    QPushButton#DeleteButton:pressed {
        background-color: #b04f55; /* Vermelho ainda mais escuro */
    }
"""

# --- Configurações do Programa ---
STATUS_OPTIONS = [ "Pendente", "Em Andamento", "Feito", "Corrigido", "Ainda não corrigido", "Feito Parcialmente", "Cancelado", "A Implementar" ]
STATUS_TEXT_COLORS = { "Pendente": QColor("#E5C07B"), "Em Andamento": QColor("#61AFEF"), "Feito": QColor("#98C379"), "Corrigido": QColor("#98C379"), "Ainda não corrigido": QColor("#E06C75"), "Feito Parcialmente": QColor("#D19A66"), "Cancelado": QColor("#5C6370"), "A Implementar": QColor("#C678DD"), }
CATEGORIES = ["A Fazer", "Correções", "Crítico / Urgente"]

def mask_pad_id(real_id):
    """Codifica o ID real do Pad para uma string Base64."""
    return base64.urlsafe_b64encode(real_id.encode('utf-8')).decode('utf-8')

def unmask_pad_id(masked_id):
    """Decodifica uma string Base64 para o ID real do Pad."""
    try:
        return base64.urlsafe_b64decode(masked_id.encode('utf-8')).decode('utf-8')
    except (ValueError, TypeError, base64.binascii.Error):
        # Retorna None se o ID for inválido/malformado
        return None

# ===================================================================
# WIDGETS E DIÁLOGOS
# ===================================================================
class ProjectCardWidget(QWidget):
    open_project = Signal(str)
    copy_link = Signal(str)
    delete_project = Signal(str)

    def __init__(self, project_data, parent=None):
        super().__init__(parent)
        self.setObjectName("ProjectCard")
        self.project_url = project_data['url']

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(8)

        name_label = QLabel(project_data.get('name', 'Projeto sem nome'))
        name_label.setObjectName("ProjectNameLabel")
        
        real_id = self.project_url.split('/')[-1]
        masked_id = mask_pad_id(real_id)

        url_label = QLabel(masked_id) # Mostra o ID mascarado
        url_label.setObjectName("ProjectUrlLabel")
        url_label.setToolTip("ID do Projeto (copie e compartilhe este ID)") # Tooltip atualizado
        
        try:
            date_obj = datetime.fromisoformat(project_data.get('last_accessed', ''))
            date_str = date_obj.strftime("Acessado em: %d/%m/%Y, %H:%M")
        except (ValueError, TypeError):
            date_str = "Data de acesso desconhecida"
        date_label = QLabel(date_str)
        date_label.setObjectName("ProjectDateLabel")

        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 10, 0, 0)
        
        copy_btn = QPushButton("Copiar ID")
        copy_btn.setObjectName("CardButton")
        copy_btn.clicked.connect(self.emit_copy_link)
        
        delete_btn = QPushButton("Excluir")
        delete_btn.setObjectName("DeleteButton")
        delete_btn.clicked.connect(self.emit_delete_project)

        open_btn = QPushButton("Abrir")
        open_btn.setObjectName("PrimaryCardButton")
        open_btn.clicked.connect(self.emit_open_project)

        button_layout.addStretch()
        button_layout.addWidget(copy_btn)
        button_layout.addWidget(delete_btn)
        button_layout.addWidget(open_btn)

        main_layout.addWidget(name_label)
        main_layout.addWidget(url_label)
        main_layout.addWidget(date_label)
        main_layout.addStretch()
        main_layout.addLayout(button_layout)
        
    def emit_open_project(self):
        self.open_project.emit(self.project_url)

    def emit_copy_link(self):
        self.copy_link.emit(self.project_url)
    
    def emit_delete_project(self):
        self.delete_project.emit(self.project_url)

class WelcomeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("WelcomeDialog")
        self.setWindowTitle("Bem-vindo ao Gerenciador de Tarefas")
        self.setMinimumSize(800, 600)
        self.selected_url = None
        self.action = None
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        sidebar_frame = QFrame()
        sidebar_frame.setObjectName("Sidebar")
        sidebar_layout = QVBoxLayout(sidebar_frame)
        sidebar_layout.setContentsMargins(15, 20, 15, 20)
        sidebar_layout.setAlignment(Qt.AlignTop)
        new_project_btn = QPushButton("Criar Novo Projeto")
        new_project_btn.setObjectName("SidebarButton")
        new_project_btn.clicked.connect(self.request_new_project)
        connect_url_btn = QPushButton("Conectar por URL")
        connect_url_btn.setObjectName("SidebarButton")
        connect_url_btn.clicked.connect(self.request_new_url)
        sidebar_layout.addWidget(new_project_btn)
        sidebar_layout.addWidget(connect_url_btn)
        sidebar_frame.setFixedWidth(220)
        main_content_widget = QWidget()
        content_layout = QVBoxLayout(main_content_widget)
        content_layout.setContentsMargins(30, 20, 30, 20)
        title_label = QLabel("Projetos Recentes")
        title_label.setObjectName("WelcomeTitle")
        self.project_list_widget = QListWidget()
        self.project_list_widget.setObjectName("ProjectList")
        self.project_list_widget.setSpacing(10)
        content_layout.addWidget(title_label)
        content_layout.addWidget(self.project_list_widget)
        main_layout.addWidget(sidebar_frame)
        main_layout.addWidget(main_content_widget, 1)

        # ADIÇÃO SUTIL: Centraliza a janela na tela
        self.move(self.screen().availableGeometry().center() - self.rect().center())
        
        self.populate_project_list()

    def populate_project_list(self):
        """
        Lê os projetos do histórico (que agora contêm 'id' em vez de 'url'),
        reconstrói a URL completa em memória e popula a lista de cards.
        """
        self.project_list_widget.clear()
        
        # A constante BASE_URL deve ser definida ou importada
        # Para simplificar, vamos defini-la aqui:
        BASE_URL = "https://pad.riseup.net/p/"
        
        projects_from_history = project_history.load_projects()
        
        if not projects_from_history:
            return

        for project_data in projects_from_history:
            # Reconstrói a URL completa para uso interno da interface
            real_url = BASE_URL + project_data.get('id', '')
            
            # Cria um dicionário temporário com a estrutura que o ProjectCardWidget espera
            card_data_for_widget = {
                'name': project_data.get('name', 'Projeto sem nome'),
                'url': real_url, # Passa a URL completa para o card
                'last_accessed': project_data.get('last_accessed', '')
            }
            
            card = ProjectCardWidget(card_data_for_widget)
            card.open_project.connect(self.on_open_project)
            card.copy_link.connect(self.on_copy_link)
            card.delete_project.connect(self.on_delete_project)
            
            list_item = QListWidgetItem(self.project_list_widget)
            list_item.setSizeHint(card.sizeHint())
            self.project_list_widget.addItem(list_item)
            self.project_list_widget.setItemWidget(list_item, card)
    
    def on_delete_project(self, url):
        """Chamado quando o botão de excluir de um card é clicado."""
        # Pergunta ao usuário para confirmar a ação
        reply = QMessageBox.question(self, "Confirmar Exclusão",
                                     "Tem certeza que deseja remover este projeto do seu histórico local?\n\n"
                                     "Isso não apagará o projeto online, apenas o atalho local.",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Se o usuário confirmar, chama a função de exclusão do backend
            project_history.delete_project(url)
            # Recarrega a lista de projetos na tela para remover o card
            self.populate_project_list()

    def on_open_project(self, url):
        self.selected_url = url; self.action = 'open'; self.accept()
    def on_copy_link(self, url):
        real_id = url.split('/')[-1]
        masked_id = mask_pad_id(real_id)
        clipboard = QApplication.instance().clipboard()
        clipboard.setText(masked_id)
        # A chamada correta, usando argumentos nomeados (keywords)
        QToolTip.showText(self.cursor().pos(), "ID copiado!", w=self, msecShowTime=2000)
    def request_new_url(self):
        self.action = 'new_url'; self.accept()
    def request_new_project(self):
        self.action = 'new_project'; self.accept()

# CÓDIGO CORRIGIDO E FUNCIONAL
class AddPadDialog(QDialog):
    """Um diálogo para o usuário adicionar o nome e a URL de um pad existente."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Adicionar Pad Existente")
        self.setMinimumWidth(500)
        
        layout = QFormLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Ex: Projeto do Cliente X")
        self.name_edit.setMaxLength(50)

        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("https://pad.riseup.net/p/exemplo-de-link")
        
        layout.addRow("Nome do Projeto:", self.name_edit)
        layout.addRow("URL do Pad:", self.url_edit)
        
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

        self.move(self.screen().availableGeometry().center() - self.rect().center())
        
    def get_data(self):
        """Retorna o nome e a URL inseridos pelo usuário."""
        name = self.name_edit.text().strip()
        url = self.url_edit.text().strip()
        return name, url

class TaskDialog(QDialog):
    def __init__(self, task=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nova Tarefa" if not task else "Editar Tarefa")
        self.setMinimumWidth(550)

        # 1. DEFINIR LIMITES DE CARACTERES
        self.TITLE_LIMIT = 100
        self.DESC_LIMIT = 1600

        self.layout = QFormLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.layout.setSpacing(10)

        # 2. APLICAR LIMITE AO TÍTULO
        self.title_edit = QLineEdit()
        self.title_edit.setMaxLength(self.TITLE_LIMIT) # Limita o campo de texto do título

        # --- Bloco de Descrição com Contador de Caracteres ---
        # Usamos um layout vertical para agrupar a caixa de texto e o contador
        desc_widget = QWidget()
        desc_layout = QVBoxLayout(desc_widget)
        desc_layout.setContentsMargins(0, 0, 0, 0)
        desc_layout.setSpacing(5)

        self.description_edit = QTextEdit()
        self.description_edit.setMinimumHeight(100)
        
        self.char_count_label = QLabel() # Label para mostrar o contador
        self.char_count_label.setAlignment(Qt.AlignRight) # Alinha o contador à direita

        desc_layout.addWidget(self.description_edit)
        desc_layout.addWidget(self.char_count_label)
        # --- Fim do Bloco de Descrição ---

        self.status_combo = QComboBox()
        self.status_combo.addItems(STATUS_OPTIONS)

        if task:
            self.title_edit.setText(task.get("title", ""))
            self.description_edit.setText(task.get("description", ""))
            self.status_combo.setCurrentText(task.get("status", "Pendente"))

        self.layout.addRow("Título:", self.title_edit)
        self.layout.addRow("Descrição:", desc_widget) # Adiciona o widget com o layout
        self.layout.addRow("Status:", self.status_combo)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept) 
        self.buttons.rejected.connect(self.reject)
        self.buttons.button(QDialogButtonBox.Ok).setStyleSheet("background-color: #98C379; color: #282c34;")
        self.buttons.button(QDialogButtonBox.Cancel).setStyleSheet("background-color: #E06C75; color: #282c34;")
        
        self.layout.addWidget(self.buttons)
        self.move(self.screen().availableGeometry().center() - self.rect().center())

        # 3. CONECTAR O SINAL DE MUDANÇA DE TEXTO PARA ATUALIZAR O CONTADOR
        self.description_edit.textChanged.connect(self.update_char_count)
        self.update_char_count() # Chama uma vez para inicializar com o valor correto

    def update_char_count(self):
        """Atualiza o contador de caracteres da descrição em tempo real."""
        count = len(self.description_edit.toPlainText())
        self.char_count_label.setText(f"{count} / {self.DESC_LIMIT}")

        # Muda a cor do contador para vermelho se o limite for excedido
        if count > self.DESC_LIMIT:
            self.char_count_label.setStyleSheet("color: #E06C75;") # Vermelho
        else:
            self.char_count_label.setStyleSheet("color: #7f848e;") # Cinza padrão

    def accept(self):
        """
        Verifica o limite de caracteres antes de permitir que a janela feche.
        """
        # 4. VALIDAR O TAMANHO DA DESCRIÇÃO ANTES DE SALVAR
        if len(self.description_edit.toPlainText()) > self.DESC_LIMIT:
            QMessageBox.warning(self, "Limite de Caracteres Excedido",
                                f"O campo 'Descrição' não pode ter mais de {self.DESC_LIMIT} caracteres.")
            return # Impede o fechamento da janela

        # Se a validação passar, fecha a janela normalmente
        super().accept()

    def get_data(self):
        return {"title": self.title_edit.text().strip(), "description": self.description_edit.toPlainText().strip(), "status": self.status_combo.currentText()}

# ===================================================================
# CLASSE: ConnectionManager
# ===================================================================
class ConnectionManager(QObject):
    tasks_updated = Signal(dict)
    operation_failed = Signal(str, object)
    operation_succeeded = Signal(str, object)
    status_update = Signal(str, int)
    connection_status_changed = Signal(bool)
    pad_created_successfully = Signal(str)

    def __init__(self):
        super().__init__()
        self.selenium_manager = None
        self.worker_thread = None
        self.action_queue = []
        self.is_connecting = False
        self.pending_action_after_finish = None

    def connect_to_pad(self, url):
        print(f"[DEBUG] Iniciando conexão com a URL real: {url}")
        if self.is_connecting or (self.worker_thread and self.worker_thread.isRunning()):
            self.status_update.emit("Aguarde a operação atual terminar.", 3000)
            return
        self.disconnect()
        self.is_connecting = True
        self.status_update.emit(f"Conectando a {url}...", 0)
        self.connection_status_changed.emit(False)
        self.selenium_manager = SeleniumManager(url)
        self.worker_thread = QThread()
        worker_task = lambda: self._run_connection_task()
        self.worker_thread.started.connect(worker_task)
        self.worker_thread.finished.connect(self._on_worker_finished)
        self.worker_thread.start()

    def _run_connection_task(self):
        if self.selenium_manager.start():
            self.status_update.emit("Conectado. Lendo tarefas...", 0)
            self.queue_action({"action": "read_tasks"})
        else:
            self.operation_failed.emit("Falha ao iniciar o navegador. Verifique o ChromeDriver.", {})
            self.disconnect()
        self.worker_thread.quit()

    def disconnect(self):
        if self.selenium_manager:
            self.selenium_manager.fechar()
            self.selenium_manager = None
            self.status_update.emit("Desconectado.", 3000)
            self.connection_status_changed.emit(False)

    def queue_action(self, payload):
        # Ação 'initialize_pad' foi trocada por 'setup_existing_pad'
        if not self.selenium_manager and payload['action'] not in ['setup_existing_pad']:
            self.operation_failed.emit("Não há conexão ativa com um projeto.", payload)
            return
        self.action_queue.append(payload)
        self._process_queue()

    def _process_queue(self):
        if (self.worker_thread and self.worker_thread.isRunning()) or not self.action_queue:
            return
        
        payload = self.action_queue.pop(0)
        self.worker_thread = QThread()
        manager_instance = None if payload['action'] == 'initialize_pad' else self.selenium_manager
        self.worker = Worker(payload, manager_instance)
        self.worker.moveToThread(self.worker_thread)

        self.worker.tasks_updated.connect(self.tasks_updated)
        self.worker.operation_failed.connect(self.operation_failed)
        self.worker.operation_succeeded.connect(self.operation_succeeded)
        self.worker.status_update.connect(lambda msg: self.status_update.emit(msg, 3000))
        
        if hasattr(self.worker, 'pad_initialized'):
            self.worker.pad_initialized.connect(self._on_pad_initialized_by_worker)

        self.worker_thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker_thread.finished.connect(self._on_worker_finished)
        self.worker_thread.finished.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)
        self.worker_thread.start()

    def _on_pad_initialized_by_worker(self, url):
        self.pad_created_successfully.emit(url)
        self.pending_action_after_finish = {'action': 'connect', 'url': url}

    def _on_worker_finished(self):
        self.worker_thread = None
        self.is_connecting = False
        
        if self.selenium_manager and self.selenium_manager.is_active():
            self.connection_status_changed.emit(True)

        if self.pending_action_after_finish:
            action_to_run = self.pending_action_after_finish
            self.pending_action_after_finish = None
            
            if action_to_run['action'] == 'connect':
                self.connect_to_pad(action_to_run['url'])
        else:
            self._process_queue()

# ===================================================================
# CLASSE: MainWindow
# ===================================================================
class MainWindow(QMainWindow):
    restart_requested = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gerenciador de Tarefas Etherpad")
        
        # ALTERAÇÃO SUTIL: Define o tamanho e depois centraliza na tela
        self.resize(1100, 800)
        self.move(self.screen().availableGeometry().center() - self.rect().center())
        
        self.pad_url = None
        self.tasks = {}
        self.last_project_keep_duration = False
        self.last_project_name_input = None
        self.connection_manager = ConnectionManager()
        self.connection_manager.tasks_updated.connect(self.on_tasks_updated)
        self.connection_manager.operation_failed.connect(self.on_operation_failed)
        self.connection_manager.operation_succeeded.connect(self.on_operation_succeeded)
        self.connection_manager.status_update.connect(self.handle_status_update)
        self.connection_manager.connection_status_changed.connect(self.on_connection_status_changed)
        self.connection_manager.pad_created_successfully.connect(self.on_pad_created)
        
        self.pending_tasks = {}
        self.sync_timer = QTimer(self)
        self.sync_timer.timeout.connect(self.sync_tasks_periodically)
        
        self.init_ui()
        self.on_connection_status_changed(False)

    def handle_status_update(self, message, timeout):
        """Filtra as mensagens da barra de status para substituir URLs por IDs."""
        prefix = "Conectando a "
        if message.startswith(prefix):
            # Extrai a URL, gera o ID e formata a nova mensagem
            url = message[len(prefix):].replace("...", "")
            real_id = url.split('/')[-1]
            masked_id = mask_pad_id(real_id)
            new_message = f"Conectando ao ID: {masked_id}..."
            self.statusBar().showMessage(new_message, timeout)
        else:
            # Para todas as outras mensagens, exibe normalmente
            self.statusBar().showMessage(message, timeout)

    def init_ui(self):
        menu_bar = self.menuBar()
        project_menu = menu_bar.addMenu("&Projeto")
        actions = [
            ("Novo Projeto Online...", self.new_project),
            ("Conectar a Projeto Online...", self.connect_to_project),
        ]
        for name, callback in actions:
            action = QAction(name, self)
            action.triggered.connect(callback)
            project_menu.addAction(action)

        self.copy_url_action = QAction("Copiar ID do Projeto", self)
        self.copy_url_action.triggered.connect(self.copy_project_url)
        project_menu.addAction(self.copy_url_action)

        project_menu.addSeparator()
        self.restart_action = QAction("Voltar à Tela Inicial", self)
        self.restart_action.triggered.connect(self.restart_application)
        project_menu.addAction(self.restart_action)
        
        project_menu.addSeparator()
        exit_action = QAction("Sair", self)
        exit_action.triggered.connect(self.close)
        project_menu.addAction(exit_action)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        self.tables = {}
        for category in CATEGORIES:
            tab = QWidget()
            self.tabs.addTab(tab, category)
            tab_layout = QVBoxLayout(tab)
            tab_layout.setContentsMargins(0, 10, 0, 0)
            
            table = QTableWidget()
            table.setColumnCount(4)
            table.setHorizontalHeaderLabels(["", "Título", "Descrição", "Status"])
            table.setColumnHidden(0, True)
            table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
            table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
            table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
            table.verticalHeader().setVisible(False)
            table.setEditTriggers(QTableWidget.NoEditTriggers)
            table.setSelectionBehavior(QTableWidget.SelectRows)
            table.setShowGrid(True)
            table.setStyleSheet("QTableView { gridline-color: #3e4451; }")
            table.doubleClicked.connect(self.edit_task)
            self.tables[category] = table
            tab_layout.addWidget(table)

            button_layout = QHBoxLayout()
            self.add_btn = QPushButton("Adicionar")
            self.edit_btn = QPushButton("Editar")
            self.del_btn = QPushButton("Excluir")
            self.del_btn.setObjectName("DeleteButton")
            self.add_btn.clicked.connect(self.add_task)
            self.edit_btn.clicked.connect(self.edit_task)
            self.del_btn.clicked.connect(self.delete_task)
            button_layout.addStretch()
            button_layout.addWidget(self.add_btn)
            button_layout.addWidget(self.edit_btn)
            button_layout.addWidget(self.del_btn)
            tab_layout.addLayout(button_layout)
        
        self.statusBar()
        QToolTip.setFont(QFont('Segoe UI', 10))
    
    def restart_application(self):
        """Emite o sinal de reinicialização e depois fecha a janela."""
        self.restart_requested.emit()
        self.close()

    def _get_project_name_from_url(self, url):
        if not url:
            return "Nenhum Projeto Conectado"
        try:
            pad_identifier = url.strip().split('/')[-1]
            last_hyphen_index = pad_identifier.rfind('-')
            if last_hyphen_index != -1:
                project_name_sanitized = pad_identifier[:last_hyphen_index]
                return project_name_sanitized.replace("_", " ")
            return pad_identifier.replace("_", " ")
        except Exception:
            return "Nome do Projeto Indisponível"

    def on_connection_status_changed(self, is_connected):
        if is_connected:
            QApplication.restoreOverrideCursor()

        self.copy_url_action.setEnabled(is_connected)
        self.tabs.setEnabled(is_connected)
        self.restart_action.setEnabled(is_connected) 
        
        if not is_connected:
            self.setWindowTitle("Gerenciador de Tarefas Etherpad")
            self.tasks = {}
            self.update_tables()
            self.sync_timer.stop()
        else:
            project_name = None
            project_id = project_history.get_id_from_url(self.pad_url)

            # LÓGICA INTELIGENTE PARA DEFINIR O NOME CORRETO
            # 1. Prioridade máxima: O nome que o usuário acabou de digitar para um novo projeto.
            if self.last_project_name_input:
                project_name = self.last_project_name_input
                self.last_project_name_input = None # Limpa a variável após o uso
            
            # 2. Segunda prioridade: O nome que já está salvo no histórico.
            if not project_name:
                project_name = project_history.get_project_name_by_id(project_id)

            # 3. Último recurso: Se não temos um nome (ex: conectar por um ID novo), "adivinha" da URL.
            if not project_name:
                project_name = self._get_project_name_from_url(self.pad_url)

            # USA O NOME CORRETO EM TODOS OS LUGARES
            self.setWindowTitle(f"Projeto: {project_name}")
            project_history.add_or_update_project(self.pad_url, project_name)
            
            if not self.sync_timer.isActive():
                self.sync_timer.start(30000)

    def start_new_project_creation(self, name, keep_pad=False):
        """Este método APENAS inicia a tarefa de backend, sem mostrar diálogos."""
        self.last_project_keep_duration = keep_pad
        payload = {"action": "initialize_pad", "palavra_alvo": name, "keep_pad": keep_pad}
        self.connection_manager.queue_action(payload)

    def new_project(self):
        """Abre um diálogo para o usuário fornecer nome e URL de um pad existente."""
        dialog = AddPadDialog(self)
        if dialog.exec():
            name, url = dialog.get_data()
            if name and url:
                # Armazena o nome para uso posterior, após a configuração do pad
                self.last_project_name_input = name
                QApplication.setOverrideCursor(Qt.WaitCursor)
                
                # Cria o payload para a nova ação de setup
                payload = {"action": "setup_existing_pad", "url": url, "name": name}
                self.connection_manager.queue_action(payload)
                return True
        return False

    def connect_to_project(self, url=None):
        """Inicia a conexão com um projeto existente (a partir de uma URL real ou de um ID mascarado)."""
        base_url = "https://pad.riseup.net/p/"
        
        if not url:
            # Pede o ID mascarado ao usuário
            masked_id, ok = QInputDialog.getText(self, "Conectar por ID", "Cole o ID do Projeto:")
            if not (ok and masked_id):
                return False
            
            # Desmascara o ID para obter o ID real
            real_id = unmask_pad_id(masked_id.strip())
            
            if not real_id:
                QMessageBox.critical(self, "Erro", "O ID fornecido é inválido ou está corrompido.")
                return False
            
            url = base_url + real_id

        self.pad_url = url.strip()
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.connection_manager.connect_to_pad(self.pad_url)
        return True

    def add_task(self):
        category, _ = self.get_current_category_and_table()
        dialog = TaskDialog(parent=self)
        if dialog.exec():
            data = dialog.get_data()
            if not data["title"]:
                QMessageBox.warning(self, "Atenção", "O campo 'Título' é obrigatório.")
                return
            new_id = str(uuid.uuid4())
            new_task = {"id": new_id, "category": category, **data}
            self.tasks[new_id] = new_task
            self.pending_tasks[new_id] = "new"
            self.update_tables()
            payload = {"action": "add_task", "data": new_task}
            self.connection_manager.queue_action(payload)

    def edit_task(self):
        _, table = self.get_current_category_and_table()
        selected_rows = table.selectionModel().selectedRows()
        if not selected_rows:
            return
        task_id = table.item(selected_rows[0].row(), 0).text()
        if task_id in self.pending_tasks:
            QMessageBox.information(self, "Aguarde", "Esta tarefa está sendo processada.")
            return
        original_task = self.tasks[task_id].copy()
        dialog = TaskDialog(original_task, self)
        if dialog.exec():
            new_data = dialog.get_data()
            if not new_data["title"]:
                return
            for key, value in new_data.items():
                if original_task.get(key) != value:
                    self.tasks[task_id][key] = value
                    self.pending_tasks[task_id] = original_task
                    self.update_tables()
                    payload = {
                        "action": "update_task",
                        "data": {"id": task_id, "campo": key, "valor": value},
                        "undo_info": {"id": task_id, "campo": key, "valor": original_task.get(key)}
                    }
                    self.connection_manager.queue_action(payload)

    def delete_task(self):
        _, table = self.get_current_category_and_table()
        selected_rows = table.selectionModel().selectedRows()
        if not selected_rows:
            return
        reply = QMessageBox.question(self, "Confirmar Exclusão", f"Excluir {len(selected_rows)} tarefa(s)?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            for row in reversed(selected_rows):
                task_id = table.item(row.row(), 0).text()
                if task_id in self.pending_tasks:
                    self.statusBar().showMessage(f"A tarefa '{self.tasks[task_id]['title']}' já está em processamento.", 3000)
                    continue
                original_task = self.tasks.pop(task_id)
                self.pending_tasks[task_id] = original_task
                self.update_tables()
                payload = {"action": "delete_task", "data": {"id": task_id}, "undo_info": original_task}
                self.connection_manager.queue_action(payload)

    def sync_tasks_periodically(self):
        if self.connection_manager.selenium_manager and self.connection_manager.selenium_manager.is_active():
            self.statusBar().showMessage("Sincronizando em segundo plano...", 2000)
            self.connection_manager.queue_action({"action": "read_tasks"})

    def on_pad_created(self, url):
        self.pad_url = url
        
        # Gera o ID mascarado a partir da URL real recebida
        real_id = url.split('/')[-1]
        masked_id = mask_pad_id(real_id)

        if self.last_project_keep_duration:
            duration_message = "O seu projeto será excluído após 365 dias de inatividade."
        else:
            duration_message = "O seu projeto será excluído após 60 dias de inatividade."
        
        # Usa o ID mascarado na mensagem para o usuário
        full_message = f"Novo projeto criado com o ID:\n{masked_id}\n\n{duration_message}\n\nConectando automaticamente..."
        
        QTimer.singleShot(0, lambda: QMessageBox.information(self, "Sucesso", full_message))
        self.last_project_keep_duration = False # Reseta a variável

    def update_tables(self):
        for table in self.tables.values():
            table.setRowCount(0)
        tasks_by_category = {cat: [] for cat in CATEGORIES}
        for task in self.tasks.values():
            if task.get("category") in tasks_by_category:
                tasks_by_category[task["category"]].append(task)
        
        for category, tasks_list in tasks_by_category.items():
            table = self.tables[category]
            table.setRowCount(len(tasks_list))
            for row, task in enumerate(sorted(tasks_list, key=lambda x: x.get('title', ''))):
                id_item = QTableWidgetItem(task["id"])
                title_item = QTableWidgetItem(task.get("title", "Sem Título"))
                desc_item = QTableWidgetItem(task.get("description", ""))
                status_item = QTableWidgetItem(task["status"])
                
                title_font = title_item.font()
                title_font.setBold(True)
                title_item.setFont(title_font)
                
                status_color = STATUS_TEXT_COLORS.get(task["status"], QColor("#abb2bf"))
                status_item.setForeground(status_color)
                status_font = status_item.font()
                status_font.setBold(True)
                status_item.setFont(status_font)
                status_item.setTextAlignment(Qt.AlignCenter)
                
                table.setItem(row, 0, id_item)
                table.setItem(row, 1, title_item)
                table.setItem(row, 2, desc_item)
                table.setItem(row, 3, status_item)

                if task["id"] in self.pending_tasks:
                    pending_color = QColor("#565f72")
                    for col in range(table.columnCount()):
                        if table.item(row, col):
                            table.item(row, col).setBackground(pending_color)

    def get_current_category_and_table(self):
        index = self.tabs.currentIndex()
        category = self.tabs.tabText(index)
        return category, self.tables[category]

    def copy_project_url(self):
        if self.pad_url:
            # Extrai o ID real da URL completa
            real_id = self.pad_url.split('/')[-1]
            # Mascara o ID e copia para a área de transferência
            masked_id = mask_pad_id(real_id)
            QApplication.clipboard().setText(masked_id)
            self.statusBar().showMessage("ID do Projeto copiado.", 3000)

    def on_tasks_updated(self, tasks):
        QApplication.restoreOverrideCursor()
        if not self.pending_tasks:
            self.tasks = tasks
        else:
            for task_id, task_data in tasks.items():
                if task_id not in self.pending_tasks:
                    self.tasks[task_id] = task_data
        
        self.update_tables()
        self.statusBar().showMessage("Tarefas sincronizadas.", 3000)

    def on_operation_succeeded(self, action, payload):
        task_id = payload['data'].get('id')
        if task_id and task_id in self.pending_tasks:
            self.pending_tasks.pop(task_id)
        
        self.update_tables()
        self.statusBar().showMessage("Ação concluída com sucesso.", 3000)

    def on_operation_failed(self, message, payload):
        QApplication.restoreOverrideCursor()
        QMessageBox.critical(self, "Erro na Operação Online", message)
        action = payload.get('action')
        task_id = None
        if action == "add_task":
            task_id = next((tid for tid, t in self.tasks.items() if tid in self.pending_tasks and payload['data'] and t['title'] == payload['data']['title']), None)
            if task_id:
                del self.tasks[task_id]
        elif action == "update_task":
            undo_info = payload.get('undo_info', {})
            task_id = undo_info.get('id')
            if task_id and task_id in self.tasks:
                self.tasks[task_id][undo_info['campo']] = undo_info['valor']
        elif action == "delete_task":
            original_task = payload.get('undo_info', {})
            task_id = original_task.get('id')
            if task_id:
                self.tasks[task_id] = original_task
        
        if task_id and task_id in self.pending_tasks:
            self.pending_tasks.pop(task_id)
            
        self.update_tables()

    def closeEvent(self, event):
        self.connection_manager.disconnect()
        event.accept()