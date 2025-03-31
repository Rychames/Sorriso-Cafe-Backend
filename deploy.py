# deploy

import requests
from decouple import config
import time
import webbrowser

class PythonAnywhereAPI:
    def __init__(self, username, api_token, project_path):
        self.username = username
        self.api_token = api_token
        self.project_path = project_path
        self.domain_name = f"{username}.pythonanywhere.com"
        self.base_url = f"https://www.pythonanywhere.com/api/v0/user/{username}/"
        self.headers = {'Authorization': f'Token {api_token}'}

        if not self.api_token:
            raise ValueError("Erro: Por favor, defina a variável de ambiente PA_API_TOKEN ou adicione-a ao seu arquivo .env com o seu token de API do PythonAnywhere.")

    def list_consoles(self):
        """Lista os consoles existentes."""
        response = requests.get(self.base_url + 'consoles/', headers=self.headers)
        if response.status_code == 200:
            return response.json()
        else:
            #print(f"Falha ao listar consoles: {response.status_code}")
            print(response.text)
            return []

    def get_active_console(self):
        """Obtém ou cria um console bash."""
        consoles = self.list_consoles()
        for console in consoles:
            console_id = console['id']
            executable = console.get('executable', '').lower()
            #print(f"Verificando console ID {console_id}: executable={executable}")
            if 'bash' in executable:
                #print(f"Usando o console com ID: {console_id}")
                return console_id

        # Nenhum console ativo foi encontrado, criar um novo
        print("Nenhum console ativo encontrado. Criando um novo console...")
        response = requests.post(
            self.base_url + 'consoles/',
            headers=self.headers,
            json={'executable': '/bin/bash'}
        )
        if response.status_code == 201:
            new_console = response.json()
            new_console_id = new_console['id']
            print(f"Novo console criado com ID: {new_console_id}. Abra-o no navegador para inicializar.")
            self.open_console_in_browser(new_console_id)
            return new_console_id
        else:
            print(f"Falha ao criar um novo console: {response.status_code}")
            print(response.text)
            return None

    def open_console_in_browser(self):
        """Abre o console no navegador."""
        console_id = self.get_active_console()
        url = f"https://www.pythonanywhere.com/user/{self.username}/consoles/{console_id}/"
        webbrowser.open(url)
        print(f"Abra o console manualmente aqui: {url}")

    def send_command(self, command, message=None):
        """Envia um comando para o console."""
        
        console_id = self.get_active_console()
        data = {'input': command + '\n'}
        response = requests.post(self.base_url + f'consoles/{console_id}/send_input/', headers=self.headers, data=data)
        if response.status_code == 200:
            if message:
                print(message)
            else:
                print(f"Comando \"{command}\" enviado com sucesso.")
        else:
            print(response.text)
            raise Exception(f"Falha ao enviar o comando \"{command}\" para o console {console_id}: {response.status_code}")

    def get_output(self):
        """Recupera a saída mais recente do console."""
        console_id = self.get_active_console()
        response = requests.get(self.base_url + f'consoles/{console_id}/get_latest_output/', headers=self.headers)
        if response.status_code == 200:
            return response.json().get('output', '')
        else:
            print(f"Falha ao obter a saída do console {console_id}: {response.status_code}")
            print(response.text)
            return ''

    def reload_webapp(self, message=None):
        if message:
            print('\n', message)
        
        response = requests.post(self.base_url + f'webapps/{self.domain_name}/reload/', headers=self.headers)
        if response.status_code == 200:
            print(f"O web app https://{self.domain_name} foi recarregado com sucesso.")
        else:
            print(f"Falha ao recarregar o web app: {response.status_code}")
            print(response.text)

    def deploy(self):
        console_id = self.get_active_console()
        if not console_id:
            print("Por favor, abra um console bash no PythonAnywhere e tente novamente.")
            return

        while True:
            self.send_command("echo 'Testando conexão'", "Testando a conexão com o console")
            
            output = self.get_output()

            if "Testando conexão" in output:
                print("Console ativo! Continuando o deploy...")
                break

            print("O console pode estar hibernado. Tentando abrir no navegador para ativá-lo...")
            self.open_console_in_browser()
            time.sleep(15)  # Dá um tempo para o usuário abrir manualmente
        
        project_directory = f"/home/{self.username}/{self.project_path}"
        
        print('\n')
        self.send_command(f"cd {project_directory}", f"Entrando no diretório do projeto: {project_directory}")
        self.send_command("git stash", "Arquivando as alterações locais...")
        self.send_command("git pull", "Atualizando os arquivos...")

        time.sleep(5)
        self.reload_webapp("Recarregando o aplicativo web...")

if __name__ == '__main__':
    USERNAME = "ppscanner"
    API_TOKEN = config('PA_API_TOKEN')
    PROJECT_PATH = 'ppscanner'
    
    try:
        pa_api = PythonAnywhereAPI(USERNAME, API_TOKEN, PROJECT_PATH)
        pa_api.deploy()
    except ValueError as e:
        print(e)
