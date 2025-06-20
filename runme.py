import subprocess
import sys
import os
from pathlib import Path
import logging
from colorama import init
from termcolor import colored
import importlib.util
import shutil
import itertools
import time

# SETTINGS
PASTA_ISOS = Path("isos")
PASTA_SAIDA = Path("xiso-unpacked")
XDVDFS_BIN = "xdvdfs.exe"
LOG_FILE = "process.log"

# Init colorama
init(autoreset=True)

REQUIRED_PACKAGES = ["colorama", "termcolor"]

def instalar_pacotes_necessarios():
    for pacote in REQUIRED_PACKAGES:
        if importlib.util.find_spec(pacote) is None:
            print(f"Installing missing package: {pacote}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pacote])

instalar_pacotes_necessarios()

def formatar_nome_pasta(nome):
    if ", The" in nome:
        nome = nome.replace(", The", "")
        nome = "The " + nome
    return nome

def encurtar_nome(nome):
    return nome[:39] + "..." if len(nome) > 42 else nome

def configurar_log():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

def mensagem_colorida(mensagem, cor='green', fundo='black', estilo='bold'):
    try:
        fundo_termcolor = f'on_{fundo}' if not fundo.startswith('on_') else fundo
        print(colored(mensagem, color=cor, on_color=fundo_termcolor, attrs=[estilo]))
    except Exception:
        print(mensagem)

def extrair_com_7z(arquivo, destino):
    try:
        comando = ["7z", "x", str(arquivo), f"-o{str(destino)}", "-y"]
        mensagem_colorida(f"Extracting {arquivo.name}", cor='cyan')
        proc = subprocess.Popen(comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        spinner = itertools.cycle(["|", "/", "-", "\\"])
        ultima_atualizacao = time.time()

        while proc.poll() is None:
            agora = time.time()
            if agora - ultima_atualizacao >= 0.2:
                print(f"Extracting... {next(spinner)}", end="\r")
                ultima_atualizacao = agora
            time.sleep(0.05)

        print("Extraction complete.         ")
        mensagem_colorida(f"{arquivo.name} extracted successfully!", cor='green')
        logging.info(f"{arquivo.name} extracted successfully.")
        return True
    except Exception as e:
        mensagem_colorida(f"Error extracting {arquivo.name}: {e}", cor='red')
        logging.error(f"Error extracting {arquivo.name}: {e}")
        return False

def unpack_iso(iso_path, destino):
    comando = [XDVDFS_BIN, "unpack", str(iso_path), str(destino)]
    try:
        mensagem_colorida(f"Unpacking ISO: {iso_path.name}", cor='yellow')
        result = subprocess.run(comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            print(f"Unpack complete at folder: {destino}")
            mensagem_colorida(f"{destino.name} unpacked successfully.", cor='green')
            logging.info(f"{destino.name} unpacked successfully.")
            return True
        else:
            mensagem_colorida(f"Error unpacking ISO: {result.stderr}", cor='red')
            logging.error(f"Error unpacking ISO {iso_path.name}: {result.stderr}")
            return False
    except Exception as e:
        mensagem_colorida(f"Error unpacking {iso_path.name}: {e}", cor='red')
        logging.error(f"Exception during unpacking {iso_path.name}: {e}")
        return False

def apagar_subpastas_vazias(caminho_base):
    for root, dirs, _ in os.walk(caminho_base, topdown=False):
        for dir in dirs:
            dir_path = Path(root) / dir
            try:
                dir_path.rmdir()
            except OSError:
                pass

def processar_isos():
    if not PASTA_ISOS.exists():
        mensagem_colorida(f"Input folder {PASTA_ISOS} not found.", cor='red')
        return False

    arquivos_validos = list(PASTA_ISOS.glob("*"))
    arquivos_processaveis = [
        arq for arq in arquivos_validos
        if arq.suffix.lower() in [".zip", ".rar", ".7z", ".7zip"]
    ]

    if not arquivos_processaveis:
        mensagem_colorida("No compressed files found to process.", cor='yellow')
        return False

    PASTA_SAIDA.mkdir(parents=True, exist_ok=True)

    for arquivo in arquivos_processaveis:
        nome_jogo = arquivo.stem
        pasta_temp = PASTA_ISOS / nome_jogo
        pasta_temp.mkdir(exist_ok=True)

        if extrair_com_7z(arquivo, pasta_temp):
            try:
                arquivo.unlink()
                mensagem_colorida(f"{arquivo.name} deleted after extraction.", cor='magenta')
            except Exception:
                pass

            pastas_criadas = []
            for iso in pasta_temp.rglob("*.iso"):
                nome_pasta = encurtar_nome(formatar_nome_pasta(iso.stem))
                destino = PASTA_SAIDA / nome_pasta
                destino.mkdir(parents=True, exist_ok=True)
                pastas_criadas.append(nome_pasta)

                if unpack_iso(iso, destino):
                    try:
                        iso.unlink()
                        mensagem_colorida(f"{iso.name} deleted after unpack.", cor='magenta')
                    except Exception:
                        pass

            apagar_subpastas_vazias(pasta_temp)
            try:
                pasta_temp.rmdir()
            except OSError:
                pass

            for nome in pastas_criadas:
                mensagem_colorida(f"Completed: {nome}", cor='cyan')
        else:
            mensagem_colorida(f"Failed to extract {arquivo.name}. Skipping...", cor='red')
            try:
                pasta_temp.rmdir()
            except OSError:
                pass

    return True

def main():
    print("Starting process...")
    configurar_log()
    houve_atividade = processar_isos()
    print("Process finished.")
    if not houve_atividade:
        mensagem_colorida("Nothing was processed. Log will not be opened.", cor='yellow')

if __name__ == "__main__":
    main()