"""
========================================================
  FERRAMENTA DE LIMPEZA E DIAGNÓSTICO DE ESTAÇÕES WINDOWS
  Versão 1.0 | Desenvolvido em Python + PyInstaller
========================================================
"""

import os
import sys
import ctypes
import shutil
import subprocess
import tempfile
import time
import glob
from datetime import datetime
from pathlib import Path


# ──────────────────────────────────────────────────────
#  UTILITÁRIOS DE CONSOLE
# ──────────────────────────────────────────────────────

class Cores:
    """Códigos ANSI para colorir o terminal."""
    RESET    = "\033[0m"
    BOLD     = "\033[1m"
    VERMELHO = "\033[91m"
    VERDE    = "\033[92m"
    AMARELO  = "\033[93m"
    AZUL     = "\033[94m"
    CIANO    = "\033[96m"
    BRANCO   = "\033[97m"
    CINZA    = "\033[90m"


def habilitar_cores_windows():
    """Ativa suporte a ANSI no terminal do Windows."""
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except Exception:
        pass


def banner():
    print(Cores.CIANO + Cores.BOLD)
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║       LIMPEZA E DIAGNÓSTICO DE ESTAÇÕES WINDOWS              ║")
    print("║       Ferramenta Automática de Manutenção v1.0               ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print(Cores.RESET)
    print(f"  {Cores.CINZA}Iniciado em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}{Cores.RESET}\n")


def secao(titulo: str):
    print()
    print(Cores.AMARELO + Cores.BOLD + f"  ▶ {titulo}")
    print("  " + "─" * 58 + Cores.RESET)


def ok(msg: str):
    print(f"  {Cores.VERDE}✔  {msg}{Cores.RESET}")


def info(msg: str):
    print(f"  {Cores.AZUL}ℹ  {msg}{Cores.RESET}")


def aviso(msg: str):
    print(f"  {Cores.AMARELO}⚠  {msg}{Cores.RESET}")


def erro(msg: str):
    print(f"  {Cores.VERMELHO}✘  {msg}{Cores.RESET}")


def rodape_resultado(arquivos: int, tamanho_mb: float):
    print(f"\n  {Cores.CINZA}┌─ Resumo ─────────────────────────────────────────────┐{Cores.RESET}")
    print(f"  {Cores.CINZA}│  Arquivos removidos : {Cores.BRANCO}{arquivos:<6}{Cores.CINZA}                            │{Cores.RESET}")
    print(f"  {Cores.CINZA}│  Espaço liberado    : {Cores.BRANCO}{tamanho_mb:.2f} MB{Cores.CINZA}                        │{Cores.RESET}")
    print(f"  {Cores.CINZA}└──────────────────────────────────────────────────────┘{Cores.RESET}")


# ──────────────────────────────────────────────────────
#  VERIFICAÇÃO DE PRIVILÉGIOS
# ──────────────────────────────────────────────────────

def verificar_administrador() -> bool:
    """Retorna True se o processo tiver privilégios de Administrador."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def relancar_como_admin():
    """Relança o executável atual com elevação UAC."""
    script = sys.executable if getattr(sys, 'frozen', False) else sys.argv[0]
    params = " ".join(f'"{a}"' for a in sys.argv[1:])
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", script, params, None, 1
    )
    sys.exit(0)


# ──────────────────────────────────────────────────────
#  1. LIMPEZA DE DIRETÓRIOS TEMPORÁRIOS
# ──────────────────────────────────────────────────────

def tamanho_arquivo_mb(caminho: str) -> float:
    """Retorna o tamanho do arquivo em MB, 0 se inacessível."""
    try:
        return os.path.getsize(caminho) / (1024 * 1024)
    except Exception:
        return 0.0


def limpar_diretorio(caminho: str) -> tuple[int, float]:
    """
    Remove recursivamente os conteúdos de um diretório.
    Retorna (quantidade_removida, megabytes_liberados).
    Ignora arquivos em uso sem travar o script.
    """
    removidos = 0
    liberados_mb = 0.0

    if not os.path.isdir(caminho):
        aviso(f"Diretório não encontrado: {caminho}")
        return removidos, liberados_mb

    for entrada in os.scandir(caminho):
        tamanho = tamanho_arquivo_mb(entrada.path)
        try:
            if entrada.is_dir(follow_symlinks=False):
                shutil.rmtree(entrada.path, ignore_errors=True)
                removidos += 1
                liberados_mb += tamanho
            else:
                os.remove(entrada.path)
                removidos += 1
                liberados_mb += tamanho
        except PermissionError:
            aviso(f"Em uso (ignorado): {os.path.basename(entrada.path)}")
        except Exception as e:
            aviso(f"Erro ao remover {os.path.basename(entrada.path)}: {e}")

    return removidos, liberados_mb


def etapa_limpeza_temporarios():
    secao("ETAPA 1 — LIMPEZA DE ARQUIVOS TEMPORÁRIOS")

    diretorios = {
        "C:\\Windows\\Temp": "C:\\Windows\\Temp",
        "%TEMP% (usuário)": os.environ.get("TEMP", ""),
        "Prefetch": "C:\\Windows\\Prefetch",
    }

    total_arqs = 0
    total_mb   = 0.0

    for nome, caminho in diretorios.items():
        if not caminho:
            aviso(f"Variável de ambiente não resolvida para: {nome}")
            continue
        info(f"Limpando: {nome} ({caminho})")
        arqs, mb = limpar_diretorio(caminho)
        ok(f"{arqs} item(ns) removido(s) — {mb:.2f} MB liberados")
        total_arqs += arqs
        total_mb   += mb

    rodape_resultado(total_arqs, total_mb)


# ──────────────────────────────────────────────────────
#  2. REPARO DE SISTEMA — SFC /SCANNOW
# ──────────────────────────────────────────────────────

def etapa_sfc():
    secao("ETAPA 2 — REPARO DE INTEGRIDADE DO SISTEMA (SFC)")
    info("Executando SFC /scannow — isso pode levar vários minutos...")
    info("Aguarde o processo concluir sem fechar esta janela.\n")

    try:
        resultado = subprocess.run(
            ["sfc", "/scannow"],
            capture_output=False,   # exibe saída em tempo real no console
            text=True,
            timeout=1800            # limite de 30 minutos
        )
        if resultado.returncode == 0:
            ok("SFC concluído com sucesso.")
        else:
            aviso(f"SFC terminou com código de saída {resultado.returncode}.")
            aviso("Verifique C:\\Windows\\Logs\\CBS\\CBS.log para detalhes.")
    except FileNotFoundError:
        erro("Comando 'sfc' não encontrado. Execute em um sistema Windows.")
    except subprocess.TimeoutExpired:
        erro("SFC excedeu o tempo limite de 30 minutos e foi interrompido.")
    except Exception as e:
        erro(f"Falha ao executar SFC: {e}")


# ──────────────────────────────────────────────────────
#  3. AGENDAMENTO DO CHKDSK /F
# ──────────────────────────────────────────────────────

def etapa_chkdsk():
    secao("ETAPA 3 — AGENDAMENTO DE VERIFICAÇÃO DE DISCO (CHKDSK)")
    info("Agendando CHKDSK /F para a próxima reinicialização...")

    try:
        # "Y\n" responde "Sim" automaticamente à pergunta de agendamento
        resultado = subprocess.run(
            ["chkdsk", "C:", "/F"],
            input="Y\n",
            capture_output=True,
            text=True,
            encoding="cp850",       # codepage padrão do prompt Windows
            errors="replace",
            timeout=60
        )
        saida = (resultado.stdout or "") + (resultado.stderr or "")
        if saida:
            for linha in saida.splitlines():
                if linha.strip():
                    print(f"  {Cores.CINZA}  {linha}{Cores.RESET}")

        ok("CHKDSK agendado — será executado na próxima reinicialização.")
        aviso("⚠  Reinicie o computador após fechar este script!")
    except FileNotFoundError:
        erro("Comando 'chkdsk' não encontrado.")
    except subprocess.TimeoutExpired:
        erro("CHKDSK demorou mais que o esperado para responder.")
    except Exception as e:
        erro(f"Falha ao agendar CHKDSK: {e}")


# ──────────────────────────────────────────────────────
#  4. FERRAMENTAS DE APOIO
# ──────────────────────────────────────────────────────

def abrir_ferramenta(nome: str, comando: list[str]):
    """Tenta abrir uma ferramenta de sistema; exibe resultado."""
    try:
        subprocess.Popen(
            comando,
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        ok(f"{nome} aberto com sucesso.")
        time.sleep(0.8)   # pequena pausa para evitar sobrecarga de abertura
    except Exception as e:
        erro(f"Não foi possível abrir {nome}: {e}")


def etapa_ferramentas_apoio():
    secao("ETAPA 4 — FERRAMENTAS DE APOIO (ANÁLISE TÉCNICA FINAL)")
    info("Abrindo ferramentas auxiliares para diagnóstico manual...")

    ferramentas = [
        ("Gerenciador de Tarefas",  ["taskmgr.exe"]),
        ("Serviços (services.msc)", ["mmc.exe", "services.msc"]),
        ("Limpeza de Disco",        ["cleanmgr.exe"]),
    ]

    for nome, cmd in ferramentas:
        abrir_ferramenta(nome, cmd)

    info("Analise os processos, serviços e itens de limpeza nas janelas abertas.")


# ──────────────────────────────────────────────────────
#  RELATÓRIO FINAL
# ──────────────────────────────────────────────────────

def relatorio_final():
    print()
    print(Cores.VERDE + Cores.BOLD)
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║               ✔  PROCESSO CONCLUÍDO COM SUCESSO             ║")
    print("╠══════════════════════════════════════════════════════════════╣")
    print("║  Próximos passos recomendados:                               ║")
    print("║  1. Feche os aplicativos desnecessários abertos.             ║")
    print("║  2. Analise o Gerenciador de Tarefas e Serviços.             ║")
    print("║  3. Execute a Limpeza de Disco para itens adicionais.        ║")
    print("║  4. REINICIE o computador para que o CHKDSK seja executado.  ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print(Cores.RESET)
    print(f"  {Cores.CINZA}Concluído em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}{Cores.RESET}\n")


# ──────────────────────────────────────────────────────
#  PONTO DE ENTRADA PRINCIPAL
# ──────────────────────────────────────────────────────

def main():
    habilitar_cores_windows()
    banner()

    # ── Verificação de privilégios ──────────────────────
    if not verificar_administrador():
        print(Cores.AMARELO + Cores.BOLD)
        print("  ⚠  Este script requer privilégios de Administrador.")
        print("     Solicitando elevação via UAC...\n" + Cores.RESET)
        time.sleep(1)
        relancar_como_admin()
        return

    ok("Executando com privilégios de Administrador.\n")

    # ── Execução das etapas ─────────────────────────────
    try:
        etapa_limpeza_temporarios()
        etapa_sfc()
        etapa_chkdsk()
        etapa_ferramentas_apoio()
        relatorio_final()
    except KeyboardInterrupt:
        print(f"\n\n  {Cores.AMARELO}Processo interrompido pelo usuário (Ctrl+C).{Cores.RESET}\n")
        sys.exit(1)

    input(f"  {Cores.CIANO}Pressione ENTER para fechar...{Cores.RESET}")


if __name__ == "__main__":
    main()
