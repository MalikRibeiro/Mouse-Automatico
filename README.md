Mouse Automático
Descrição
Mouse Automático é uma aplicação Python que permite gravar e reproduzir macros de mouse e teclado. Com uma interface gráfica intuitiva, os usuários podem gravar sequências de ações (movimentos do mouse, cliques, rolagens e pressionamentos de teclas) e reproduzi-las em loops com atrasos configuráveis. As macros são salvas em arquivos JSON para reutilização.
Funcionalidades

Gravação de Macros: Captura movimentos do mouse, cliques, rolagens e pressionamentos de teclas.
Reprodução de Macros: Executa macros salvas em loops com atrasos configuráveis.
Interface Gráfica: Interface amigável com botões para gravar, reproduzir, parar e configurar atalhos.
Atalhos de Teclado: Atalhos configuráveis para iniciar/parar gravação e reprodução.
Resolução Adaptável: Ajusta automaticamente as coordenadas do mouse para diferentes resoluções de tela.
Salvamento de Macros: Macros são salvas em arquivos JSON na pasta macros.

Requisitos

Python 3.6+
Bibliotecas Python:
pynput
keyboard
pyautogui
tkinter (geralmente incluído com Python)


Sistema operacional: Windows, macOS ou Linux (testado em Windows)

Instalação

Clone ou baixe este repositório.
Instale as dependências necessárias:pip install pynput keyboard pyautogui


Execute o script principal:python v03.py



Como Usar

Iniciar o Programa:
Execute v03.py para abrir a interface gráfica.


Gravar uma Macro:
Clique em "Gravar" ou use o atalho padrão (Ctrl+3).
Realize as ações desejadas (movimentos do mouse, cliques, rolagens, teclas).
Clique em "Parar Gravação" ou use o atalho de parada (Esc).
Insira um nome para salvar a macro como um arquivo JSON.


Reproduzir uma Macro:
Clique em "Play Macro" ou use o atalho padrão (Ctrl+1).
Selecione o arquivo JSON da macro na pasta macros.
A macro será executada em loop até ser interrompida.


Parar a Execução:
Clique em "Parar Execução" ou use o atalho padrão (Esc).


Configurar Atalhos:
Clique em "Configurar Atalhos" para personalizar os atalhos de teclado.


Local de Salvamento:
As macros são salvas na pasta macros no mesmo diretório do script.



Atalhos Padrão

Gravar/Parar Gravação: Ctrl+3
Reproduzir/Parar Reprodução: Ctrl+1
Parar Tudo: Esc

Estrutura do Projeto

v03.py: Script principal contendo a lógica da aplicação e a interface gráfica.
macros/: Pasta onde as macros são salvas como arquivos JSON.

Exemplo de Arquivo de Macro
As macros são salvas em formato JSON com a seguinte estrutura:
{
  "resolution": [1920, 1080],
  "events": [
    {"action": "move", "x": 0.5, "y": 0.5, "time": 1.23},
    {"action": "press_btn", "button": "Button.left", "x": 0.5, "y": 0.5, "time": 1.25},
    {"action": "press", "key": "a", "time": 1.30}
  ]
}

Notas

Resolução de Tela: As coordenadas do mouse são normalizadas com base na resolução da tela durante a gravação, permitindo adaptação a diferentes resoluções na reprodução.
Segurança: Certifique-se de que as macros sejam usadas em ambientes controlados, pois a automação pode interagir com outros aplicativos de forma inesperada.
Permissões: Em alguns sistemas, pode ser necessário executar o script com privilégios de administrador para capturar eventos de teclado/mouse.

Contribuições
Contribuições são bem-vindas! Para sugerir melhorias ou relatar bugs:

Fork o repositório.
Crie uma branch para sua feature (git checkout -b feature/nova-funcionalidade).
Commit suas alterações (git commit -m 'Adiciona nova funcionalidade').
Envie para o repositório remoto (git push origin feature/nova-funcionalidade).
Abra um Pull Request.

Autor
Desenvolvido por Malik Ribeiro Mourad.
Licença
Este projeto é licenciado sob a MIT License.
