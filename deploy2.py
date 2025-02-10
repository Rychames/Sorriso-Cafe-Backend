import requests

API_TOKEN = "e5486a3695e7facb5bd6b50cca1fdaddd9f29b43"
USERNAME = "ppscanner"

def run_command(command):
    url = f"https://www.pythonanywhere.com/api/v0/user/{USERNAME}/consoles/"
    headers = {"Authorization": f"Token {API_TOKEN}"}

    response = requests.post(url, json={"executable": "/bin/bash"}, headers=headers)

    print("Resposta da API:", response.text) 

    console_id = response.json()["id"]


    # Criar um novo console Bash
    response = requests.post(url, json={"executable": "/bin/bash"}, headers=headers)
    console_id = response.json()["id"]

    # Executar comando no console
    command_url = f"{url}{console_id}/send_input/"
    requests.post(command_url, json={"input": command + "\n"}, headers=headers)

    # Obter saída do console
    output_url = f"{url}{console_id}/get_latest_output/"
    output_response = requests.get(output_url, headers=headers)

    return output_response.text

# Testando
print(run_command("ls -la"))
