import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
# A importação de NewProjectDialog foi removida para corrigir o erro
from gui import MainWindow, WelcomeDialog, STYLE_SHEET


# Variáveis globais para manter a referência das janelas ativas
main_window = None
welcome_dialog = None

def run_application():
    """Cria e configura a janela principal com base na escolha do usuário."""
    global main_window, welcome_dialog

    if welcome_dialog:
        action = welcome_dialog.action
        selected_url = welcome_dialog.selected_url
        welcome_dialog.close()
    else:
        app.quit()
        return

    main_window = MainWindow()
    main_window.restart_requested.connect(show_welcome_dialog)
    
    action_initiated = False
    
    if action == 'open':
        if main_window.connect_to_project(selected_url):
            action_initiated = True

    elif action == 'new_url':
        if main_window.connect_to_project():
            action_initiated = True
    
    elif action == 'new_project':
        # Esta chamada agora abre o novo diálogo "AddPadDialog" dentro da MainWindow
        if main_window.new_project():
            action_initiated = True

    if action_initiated:
        main_window.show()
    else:
        # Se a ação foi cancelada (ex: fechar o diálogo), volta para a tela inicial
        show_welcome_dialog()


def show_welcome_dialog():
    """Cria e mostra a tela de boas-vindas."""
    global welcome_dialog, main_window
    
    if main_window:
        main_window.deleteLater()

    welcome_dialog = WelcomeDialog()
    welcome_dialog.accepted.connect(run_application)
    welcome_dialog.rejected.connect(app.quit)
    welcome_dialog.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Define o ícone global da aplicação
    app_icon = QIcon("app_icon.ico")
    app.setWindowIcon(app_icon)
    
    app.setStyleSheet(STYLE_SHEET)

    show_welcome_dialog()
    
    sys.exit(app.exec())