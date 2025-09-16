# Gerenciador de Tarefas com Etherpad

![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)
![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)
![Status](https://img.shields.io/badge/Status-Est%C3%A1vel-brightgreen)

Um gerenciador de tarefas desktop, colaborativo e anônimo que utiliza instâncias públicas de **Etherpad** como um banco de dados em tempo real, sem a necessidade de cadastro ou servidor próprio.

---

## Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Funcionalidades](#funcionalidades)
- [Como Usar (Usuário Final)](#como-usar-usuário-final)
- [Compilação (Para Desenvolvedores)](#compilação-para-desenvolvedores)
- [Como Funciona](#como-funciona)
- [Instâncias de Etherpad e Conexão](#instâncias-de-etherpad-e-conexão)
- [Termos de Serviço e Recomendações de Segurança](#termos-de-serviço-e-recomendações-de-segurança)
- [Licença](#licença)

---

## Sobre o Projeto

Este projeto nasceu da necessidade de ter uma ferramenta de gestão de tarefas simples, ao estilo Kanban, que fosse colaborativa, gratuita e que não exigisse a criação de contas ou a configuração de um backend complexo.

A solução foi utilizar a plataforma **Etherpad Lite** como um banco de dados JSON "improvisado". A aplicação controla um navegador web em segundo plano para ler e escrever tarefas de forma estruturada em um pad público, permitindo que múltiplos usuários, em diferentes computadores, possam colaborar nas mesmas tarefas apenas compartilhando um link mascarado.

## Funcionalidades

- **Sem Cadastro, Sem Login**: Totalmente anônimo. Crie um projeto e comece a usar.
- **Colaboração em Tempo Real**: Múltiplos usuários podem visualizar e editar a mesma lista de tarefas simultaneamente.
- **Interface Moderna**: Uma interface desktop com tema escuro, construída com PySide6.
- **Compartilhamento Seguro**: Os links para os pads são mascarados em Base64 para um compartilhamento mais limpo e menos óbvio.
- **Organização por Categorias**: Organize suas tarefas em abas personalizáveis (ex: "A Fazer", "Correções", "Crítico / Urgente").
- **Ampla Compatibilidade**: Conecte-se a praticamente qualquer instância pública de Etherpad.
- **Histórico Local**: A aplicação salva um histórico dos projetos que você acessou para reconexão rápida.

---

## Como Usar (Usuário Final)

Para a maioria dos usuários, basta baixar e executar.

1.  Acesse a seção **[Releases](https://github.com/matheusaraujoc/Pad-Tasks/releases)** deste repositório.
2.  Baixe o arquivo executável para o seu sistema operacional (ex: `Pad-Tasks-v1.0.0-win64.exe` para Windows).
3.  Execute o arquivo. Não é necessária instalação.

Obs: Para o projeto ser criado, o pad deve está limpo.

### ⚠️ Aviso para Usuários Windows (Filtro SmartScreen)

Ao executar o programa pela primeira vez, é provável que o Windows Defender SmartScreen exiba uma tela azul impedindo a execução, com a mensagem "O Windows protegeu o computador".

**Isso é um comportamento normal e esperado.** Acontece porque o aplicativo não possui uma assinatura digital de uma empresa registrada na Microsoft. **O programa é seguro e não contém vírus.**

Para executar, siga estes passos:
1. Na tela azul, clique em **"Mais informações"**.
2. Um novo botão, **"Executar assim mesmo"**, aparecerá. Clique nele.

Você só precisará fazer isso na primeira vez que abrir o programa.

---

## Compilação (Para Desenvolvedores)

Se você deseja modificar o código, compilá-lo ou executá-lo a partir da fonte, siga os passos abaixo.

### Pré-requisitos

1.  **Python 3.9 ou superior** instalado.
2.  **Google Chrome** instalado em seu sistema.
3.  **ChromeDriver** correspondente à sua versão do Google Chrome.
    -   Faça o download em: [https://googlechromelabs.github.io/chrome-for-testing/](https://googlechromelabs.github.io/chrome-for-testing/)
    -   **Importante:** Após o download, extraia o `chromedriver.exe` (ou `chromedriver` em Linux/macOS) e coloque o arquivo em uma pasta que esteja no `PATH` do seu sistema para que o Selenium possa encontrá-lo.

### Passos para Execução

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/matheusaraujoc/Pad-Tasks.git](https://github.com/matheusaraujoc/Pad-Tasks.git)
    cd seu-repositorio
    ```

2.  **Crie e ative um ambiente virtual (recomendado):**
    ```bash
    # Para Windows
    python -m venv venv
    .\venv\Scripts\activate

    # Para Linux/macOS
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Instale as dependências:**
    Crie um arquivo chamado `requirements.txt` na raiz do projeto com o seguinte conteúdo:
    ```txt
    PySide6
    selenium
    ```
    Em seguida, instale as dependências com o pip:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Execute a aplicação:**
    ```bash
    python main.py
    ```
---

## Como Funciona

A magia do projeto está em sua arquitetura cliente-servidor "sem servidor".

1.  **Backend (Etherpad)**: Um pad em uma instância pública de Etherpad é tratado como um arquivo de texto bruto.
2.  **Formato dos Dados**: As tarefas são estruturadas como um objeto JSON e salvas como texto puro dentro do pad.
3.  **Cliente (Selenium)**: A aplicação desktop usa o Selenium para controlar uma instância oculta (headless) do Google Chrome. Este navegador acessa a URL do pad.
4.  **Operações "Cirúrgicas"**: Em vez de ler o JSON, modificar e reescrever o arquivo inteiro (o que seria lento e propenso a conflitos), a aplicação realiza edições "cirúrgicas". Ela usa JavaScript injetado via Selenium para encontrar e substituir apenas os trechos de texto exatos correspondentes a uma tarefa ou campo, tornando as atualizações quase instantâneas.
5.  **Mecanismo de Lock**: Para evitar que duas instâncias do aplicativo tentem escrever no pad exatamente ao mesmo tempo (uma condição de corrida), um sistema de "lock" é implementado. Antes de qualquer escrita, a aplicação adiciona uma marcação na primeira linha do pad (ex: `[LOCK-by-user-uuid-at-timestamp]`). Outras instâncias verão essa marcação, aguardarão sua remoção e só então tentarão realizar sua própria escrita. Isso garante a integridade do JSON.

---

## Instâncias de Etherpad e Conexão

**O que é uma instância de Etherpad?**
É um site que hospeda o software de edição de texto colaborativo Etherpad Lite. Existem centenas de instâncias públicas e gratuitas mantidas pela comunidade ao redor do mundo. Esta aplicação foi projetada para ser compatível com a maioria delas.

### Instâncias Testadas

As seguintes instâncias foram testadas e funcionaram corretamente durante o desenvolvimento:

-   **yopad.eu**: `https://yopad.eu/`
-   **Riseup Pad**: `https://pad.riseup.net/`
-   **Wikimedia Etherpad**: `https://etherpad.wikimedia.org/`
-   **Framapad**: `https://annuel.framapad.org/`
-   **Pad.education**: `https://pad.education/`

### Testando Outras Instâncias

Você pode encontrar uma lista extensa de instâncias públicas e testá-las por conta própria. A comunidade do Etherpad mantém uma lista na wiki do seu repositório:

-   [Sites que rodam Etherpad (GitHub Wiki)](https://github.com/ether/etherpad-lite/wiki/Sites-That-Run-Etherpad)

---

## Termos de Serviço e Recomendações de Segurança

1.  Este software é fornecido "COMO ESTÁ", sem garantias de qualquer tipo. O desenvolvedor não se responsabiliza por qualquer perda de dados que possa ocorrer.
2.  **O usuário é o único e total responsável pelo seu pad, incluindo a gestão de seu acesso e segurança.**
3.  O usuário deve cumprir os termos de uso específicos de cada instância de Etherpad que escolher utilizar.
4.  **Recomendação de Segurança**: A segurança do seu pad depende da complexidade do seu link. Se a instância de Etherpad escolhida não gerar nomes de pads aleatórios e complexos por padrão, é **altamente recomendável** que você crie nomes longos e aleatórios (utilizando geradores de senhas ou tokens) para o seu pad.
    -   *Exemplo ruim:* `reuniao-cliente`
    -   *Exemplo bom:* `meu-projeto-secreto-7k2j9f5b3p`
    Isso dificulta que pessoas não autorizadas adivinhem o link do seu pad. Felizmente, a maioria das instâncias modernas já oferece a criação de pads com nomes aleatórios.
5.  **Aviso sobre Retenção de Dados**: A disponibilidade e as políticas de retenção de dados das instâncias públicas estão fora do controle deste projeto. Muitos servidores gratuitos podem apagar pads inativos. **Use este software ciente de que seus dados podem não ser permanentes.**

---

## Licença

Este projeto e seu código-fonte são licenciados sob a **Creative Commons Atribuição-NãoComercial-CompartilhaIgual 4.0 Internacional (CC BY-NC-SA 4.0)**.

[![CC BY-NC-SA 4.0](https://licensebuttons.net/l/by-nc-sa/4.0/88x31.png)](http://creativecommons.org/licenses/by-nc-sa/4.0/)

Isso significa que você tem a liberdade de:

-   **Compartilhar** — copiar e redistribuir o material em qualquer suporte ou formato.
-   **Adaptar** — remixar, transformar e criar a partir do material.

Sob os seguintes termos:

-   **Atribuição** — Você deve dar o **crédito apropriado** a **Matheus Araújo Carvalho**, prover um link para a licença e indicar se foram feitas alterações.
-   **NãoComercial** — Você **não pode** usar o material para fins comerciais.
-   **CompartilhaIgual** — Se você remixar, transformar ou criar a partir do material, deverá distribuir suas contribuições sob a **mesma licença** que o original.

Para ver uma cópia completa desta licença, visite:
[http://creativecommons.org/licenses/by-nc-sa/4.0/](http://creativecommons.org/licenses/by-nc-sa/4.0/)
