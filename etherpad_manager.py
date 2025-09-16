# etherpad_manager.py
import sys
import secrets
import time
import json
import uuid
import re
from threading import Thread

from PySide6.QtCore import QObject, Signal, QThread

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException


# ===================================================================
# CONSTANTES PARA O MECANISMO DE LOCK
# ===================================================================
LOCK_TIMEOUT_SECONDS = 30
LOCK_RETRY_DELAY_SECONDS = 3
MAX_LOCK_RETRIES = 5
LOCK_REGEX = re.compile(r"\[LOCK-by-([a-f0-9\-]+)-at-([\d\.]+)\]\n?")


# ===================================================================
# CLASSE DE AUTOMAÇÃO COM SELENIUM (VERSÃO 100% CIRÚRGICA)
# ===================================================================
class SeleniumManager:
    """
    Gerencia uma ÚNICA instância do navegador Selenium. TODAS as operações de
    escrita, incluindo o lock, são "cirúrgicas" para máxima performance.
    NÃO HÁ REESCRITA COMPLETA DO DOCUMENTO.
    """
    def __init__(self, url):
        self.url = url
        self.driver = None
        self.user_id = str(uuid.uuid4())

    def start(self):
        if self.driver: return True
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--log-level=3")
            chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
            self.driver = webdriver.Chrome(options=chrome_options)
            self._navegar_para_editor()
            return True
        except WebDriverException as e:
            print(f"Erro ao iniciar o Selenium: {e}")
            self.driver = None
            return False

    def is_active(self):
        return self.driver is not None

    def fechar(self):
        if self.driver:
            self.release_lock()
            self.driver.quit()
            self.driver = None

    def _navegar_para_editor(self):
        try:
            self.driver.switch_to.default_content()
            WebDriverWait(self.driver, 1).until(EC.frame_to_be_available_and_switch_to_it((By.NAME, "ace_outer")))
            WebDriverWait(self.driver, 1).until(EC.frame_to_be_available_and_switch_to_it((By.NAME, "ace_inner")))
        except TimeoutException:
            self.driver.get(self.url)

            # --- INÍCIO DA CORREÇÃO PARA O DISROOT ---
            # Procura pelo banner de cookies e o aceita, se existir.
            # Usamos um timeout curto e um try/except para não quebrar em sites que não têm o banner.
            try:
                cookie_banner_accept_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "cc-allow"))
                )
                cookie_banner_accept_button.click()
                time.sleep(1) # Pequena pausa para a animação do banner desaparecer
            except TimeoutException:
                # O banner não foi encontrado, o que é normal em outros sites. Segue o fluxo.
                pass
            # --- FIM DA CORREÇÃO ---

            # Continua com a lógica original de encontrar os iframes do editor
            WebDriverWait(self.driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.NAME, "ace_outer")))
            WebDriverWait(self.driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.NAME, "ace_inner")))
        
        return WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "innerdocbody")))

    # <--- INÍCIO DA ADIÇÃO: MÉTODOS ROBUSTOS DE ESCRITA E LIMPEZA --->
    def escrever_no_pad(self, texto):
        """
        Método robusto para escrever texto simulando a digitação do usuário.
        """
        editor = self._navegar_para_editor()
        editor.click()
        time.sleep(0.2)
        editor.send_keys(texto)
        time.sleep(0.5)
        return True

    def limpar_pad(self):
        """
        Método robusto para limpar todo o conteúdo do pad.
        """
        editor = self._navegar_para_editor()
        editor.click()
        time.sleep(0.2)
        # Define a tecla de atalho para "Selecionar Tudo" (Ctrl+A ou Cmd+A)
        select_all_key = Keys.COMMAND if sys.platform == 'darwin' else Keys.CONTROL
        editor.send_keys(select_all_key + 'a')
        time.sleep(0.2)
        editor.send_keys(Keys.BACKSPACE)
        time.sleep(0.5)
        return True
    # <--- FIM DA ADIÇÃO --->

    # --- FERRAMENTAS CIRÚRGICAS DE BAIXO NÍVEL ---
    def _get_raw_pad_text_js(self):
        editor = self._navegar_para_editor()
        return self.driver.execute_script("return arguments[0].innerText;", editor)
    
    def _read_first_line(self):
        text = self._get_raw_pad_text_js()
        return text.split('\n', 1)[0]

    def _insert_text_at_start(self, text):
        editor = self._navegar_para_editor()
        js_script = """
            var editor = arguments[0];
            var sel = window.getSelection();
            var range = document.createRange();
            range.selectNodeContents(editor);
            range.collapse(true);
            sel.removeAllRanges();
            sel.addRange(range);
            editor.focus();
        """
        self.driver.execute_script(js_script, editor)
        editor.send_keys(text)
        time.sleep(0.5)

    def achar_e_substituir(self, palavra_alvo, texto_substituto, occurrence_index=0):
        try:
            editor = self._navegar_para_editor()
            js_script = """
                var editor = arguments[0], targetWord = arguments[1], occurrence = arguments[2];
                var sel = window.getSelection();
                sel.removeAllRanges();
                var range = document.createRange();
                range.selectNodeContents(editor);
                range.collapse(true);
                sel.addRange(range);
                editor.focus();
                var found = false;
                for (var i = 0; i <= occurrence; i++) {
                    found = window.find(targetWord, true, false, true, false, false, false);
                    if (!found) break;
                }
                return found;
            """
            found = self.driver.execute_script(js_script, editor, palavra_alvo, occurrence_index)
            if not found:
                return False
            
            time.sleep(0.3)
            editor.send_keys(texto_substituto if texto_substituto else Keys.BACKSPACE)
            time.sleep(0.5)
            return True
        except Exception as e:
            print(f"Ocorreu um erro em achar_e_substituir: {e}")
            return False

    def _remove_text_at_start_js(self, text_to_remove):
        editor = self._navegar_para_editor()
        js_script = """
            var editor = arguments[0];
            var targetText = arguments[1];
            var currentText = editor.innerText;

            if (currentText.startsWith(targetText)) {
                editor.innerText = currentText.substring(targetText.length);
                return true;
            }
            return false;
        """
        success = self.driver.execute_script(js_script, editor, text_to_remove)
        time.sleep(0.5)
        return success

    # --- MECANISMO DE LOCK 100% CIRÚRGICO ---
    def _parse_lock(self, text):
        return LOCK_REGEX.match(text)

    def acquire_lock(self):
        first_line = self._read_first_line()
        existing_lock = self._parse_lock(first_line)
        my_lock_str = f"[LOCK-by-{self.user_id}-at-{time.time()}]"
        my_lock_str_with_newline = my_lock_str + '\n'

        if existing_lock:
            lock_owner_id = existing_lock.group(1)
            lock_timestamp = float(existing_lock.group(2))

            if lock_owner_id == self.user_id:
                return True

            if time.time() - lock_timestamp > LOCK_TIMEOUT_SECONDS:
                print("Lock vencido encontrado. Sobrescrevendo cirurgicamente...")
                old_lock_str = existing_lock.group(0).strip()
                return self.achar_e_substituir(old_lock_str, my_lock_str)
            else:
                print("Pad está travado por outro usuário. Aguardando...")
                return False
        else:
            self._insert_text_at_start(my_lock_str_with_newline)
            time.sleep(0.2)
            new_first_line = self._read_first_line()
            if new_first_line.strip() == my_lock_str:
                print("Lock adquirido com sucesso.")
                return True
            else:
                print("Falha ao adquirir lock (concorrência detectada). Limpando...")
                self.achar_e_substituir(my_lock_str_with_newline, "")
                return False

    def release_lock(self):
        first_line = self._read_first_line()
        existing_lock = self._parse_lock(first_line)
        if existing_lock and existing_lock.group(1) == self.user_id:
            lock_to_remove = existing_lock.group(0) + '\n'
            print("Liberando lock cirurgicamente...")
            if not self._remove_text_at_start_js(lock_to_remove):
                print("AVISO: A remoção cirúrgica do lock via JS falhou.")
        return True

    # --- MÉTODOS PÚBLICOS (TODOS CIRÚRGICOS) ---
    def ler_do_pad(self):
        raw_text = self._get_raw_pad_text_js()
        return LOCK_REGEX.sub('', raw_text)

    def _to_minified_multiline_json(self, data):
        minified = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
        return minified.replace('},"', '},\n"')

    def atualizar_tarefa_json(self, id_tarefa, campo_modificar, novo_valor):
        for attempt in range(MAX_LOCK_RETRIES):
            if self.acquire_lock():
                try:
                    texto_atual = self.ler_do_pad().strip()
                    if not texto_atual: return "nao_encontrado"
                    try: dados = json.loads(texto_atual)
                    except json.JSONDecodeError: return "json_invalido"

                    if id_tarefa not in dados or campo_modificar not in dados[id_tarefa]:
                        return "campo_nao_encontrado"
                    
                    valor_original = dados[id_tarefa][campo_modificar]
                    str_original = f'"{campo_modificar}":{json.dumps(valor_original, ensure_ascii=False)}'
                    str_novo = f'"{campo_modificar}":{json.dumps(novo_valor, ensure_ascii=False)}'
                    
                    anchor_str = f'"{id_tarefa}":{{'
                    task_start_index = texto_atual.find(anchor_str)
                    if task_start_index == -1: return "substituicao_falhou"

                    target_index = texto_atual.find(str_original, task_start_index)
                    if target_index == -1: return "valor_ja_modificado"

                    occurrence_index = texto_atual.count(str_original, 0, target_index)

                    if self.achar_e_substituir(str_original, str_novo, occurrence_index):
                        return "sucesso"
                    else:
                        return "substituicao_falhou"
                finally:
                    self.release_lock()
            else:
                time.sleep(LOCK_RETRY_DELAY_SECONDS)
        return "lock_timeout"

    def criar_nova_tarefa_json(self, dados_tarefa):
        for attempt in range(MAX_LOCK_RETRIES):
            if self.acquire_lock():
                try:
                    texto_atual = self.ler_do_pad().strip()

                    if not texto_atual or texto_atual == '{}':
                        novo_id = dados_tarefa.get("id", str(uuid.uuid4()))
                        dados_iniciais = {novo_id: {**dados_tarefa, "id": novo_id}}
                        texto_json = self._to_minified_multiline_json(dados_iniciais)
                        
                        # Limpa o pad e escreve o conteúdo inicial
                        self.limpar_pad()
                        self.escrever_no_pad(texto_json)
                        return "sucesso"

                    try: json.loads(texto_atual)
                    except json.JSONDecodeError: return "json_invalido"

                    novo_id = dados_tarefa.get("id", str(uuid.uuid4()))
                    nova_tarefa_obj = {**dados_tarefa, "id": novo_id}
                    
                    fragmento_str = json.dumps({novo_id: nova_tarefa_obj}, separators=(',', ':'), ensure_ascii=False)
                    texto_para_inserir = ",\n" + fragmento_str[1:-1]

                    if self.achar_e_substituir("}", texto_para_inserir + "}", occurrence_index=texto_atual.count("}") - 1):
                        return "sucesso"
                    else:
                        print("ERRO: Não foi possível encontrar a chave '}' final no pad.")
                        return "erro_geral"
                finally:
                    self.release_lock()
            else:
                time.sleep(LOCK_RETRY_DELAY_SECONDS)
        return "lock_timeout"

    def apagar_tarefa_json(self, id_tarefa):
        for attempt in range(MAX_LOCK_RETRIES):
            if self.acquire_lock():
                try:
                    texto_atual = self.ler_do_pad().strip()
                    if not texto_atual: return "nao_encontrado"
                    try: dados = json.loads(texto_atual)
                    except json.JSONDecodeError: return "json_invalido"
                    if id_tarefa not in dados: return "nao_encontrado"

                    tarefa_obj = dados[id_tarefa]
                    fragmento_tarefa_str = f'"{id_tarefa}":{json.dumps(tarefa_obj, separators=(",", ":"), ensure_ascii=False)}'
                    
                    bloco_para_apagar = None
                    if texto_atual.find(fragmento_tarefa_str + ",\n") != -1:
                        bloco_para_apagar = fragmento_tarefa_str + ",\n"
                    elif texto_atual.find(",\n" + fragmento_tarefa_str) != -1:
                        bloco_para_apagar = ",\n" + fragmento_tarefa_str
                    else:
                        bloco_para_apagar = fragmento_tarefa_str

                    if self.achar_e_substituir(bloco_para_apagar, ""):
                        if len(dados) == 1:
                            self.limpar_pad()
                            self.escrever_no_pad("{}")
                        return "sucesso"
                    else:
                        return "substituicao_falhou"
                finally:
                    self.release_lock()
            else:
                time.sleep(LOCK_RETRY_DELAY_SECONDS)
        return "lock_timeout"

# ===================================================================
# CLASSE WORKER
# ===================================================================
class Worker(QObject):
    operation_succeeded = Signal(str, object)
    operation_failed = Signal(str, object)
    tasks_updated = Signal(dict)
    pad_initialized = Signal(str)
    status_update = Signal(str)
    finished = Signal()

    def __init__(self, payload, selenium_manager=None):
        super().__init__()
        self.manager = selenium_manager
        self.payload = payload
        self.acao = payload.get('action')

    def run(self):
        if self.acao == "setup_existing_pad":
            self.run_setup_existing_pad()
            return
        
        try:
            if not self.manager or not self.manager.is_active():
                raise Exception("Selenium Manager não está ativo ou conectado.")

            if self.acao == "read_tasks":
                self.status_update.emit("Lendo tarefas do Pad...")
                texto = self.manager.ler_do_pad()
                try:
                    tasks = json.loads(texto) if texto and texto.strip() else {}
                    self.tasks_updated.emit(tasks)
                except json.JSONDecodeError as e:
                    self.operation_failed.emit(f"O conteúdo do Pad não é um JSON válido: {e}", self.payload)

            elif self.acao == "add_task":
                self.status_update.emit("Criando nova tarefa no pad...")
                resultado = self.manager.criar_nova_tarefa_json(self.payload['data'])
                if resultado == "sucesso":
                    self.operation_succeeded.emit(self.acao, self.payload)
                else:
                    self.operation_failed.emit(f"Falha ao criar tarefa: {resultado}", self.payload)
            
            elif self.acao == "update_task":
                task_data = self.payload['data']
                self.status_update.emit(f"Atualizando tarefa ID {task_data['id']}...")
                resultado = self.manager.atualizar_tarefa_json(
                    task_data['id'], task_data['campo'], task_data['valor'])
                if resultado == "sucesso":
                    self.operation_succeeded.emit(self.acao, self.payload)
                else:
                    self.operation_failed.emit(f"Falha ao atualizar tarefa: {resultado}", self.payload)

            elif self.acao == "delete_task":
                task_data = self.payload['data']
                self.status_update.emit(f"Apagando tarefa ID {task_data['id']}...")
                resultado = self.manager.apagar_tarefa_json(task_data['id'])
                if resultado == "sucesso":
                    self.operation_succeeded.emit(self.acao, self.payload)
                else:
                    self.operation_failed.emit(f"Falha ao apagar tarefa: {resultado}", self.payload)

            if self.acao in ["add_task", "update_task", "delete_task"]:
                self.status_update.emit("Sincronizando tarefas...")
                texto = self.manager.ler_do_pad()
                tasks = json.loads(texto) if texto and texto.strip() else {}
                self.tasks_updated.emit(tasks)

        except TimeoutException:
            self.operation_failed.emit("Erro: O tempo de espera foi excedido.", self.payload)
        except Exception as e:
            self.operation_failed.emit(f"Ocorreu um erro inesperado: {e}", self.payload)
        finally:
            self.finished.emit()

    def run_setup_existing_pad(self):
        """Conecta a um pad existente, verifica se está vazio e o inicializa."""
        temp_manager = None
        try:
            url = self.payload['url']
            self.status_update.emit(f"Configurando pad em {url}...")
            
            temp_manager = SeleniumManager(url)
            if not temp_manager.start():
                raise Exception("Não foi possível conectar ao Pad. Verifique a URL.")

            # Verifica se o pad está realmente vazio antes de formatá-lo
            texto_atual = temp_manager.ler_do_pad().strip()
            if texto_atual != "" and texto_atual != "{}":
                raise Exception("O Pad fornecido não está vazio. Por segurança, use um Pad novo e em branco.")

            # Se estiver vazio ou já inicializado, formata e prepara para uso
            self.status_update.emit("Inicializando o pad como banco de dados...")
            temp_manager.limpar_pad()
            temp_manager.escrever_no_pad("{}")
            
            # Sinaliza que o pad foi "criado" (configurado) com sucesso
            self.pad_initialized.emit(url)

        except Exception as e:
            self.operation_failed.emit(f"Falha ao configurar o pad: {e}", self.payload)
        finally:
            if temp_manager:
                temp_manager.fechar()
            self.finished.emit()