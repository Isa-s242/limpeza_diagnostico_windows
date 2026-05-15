# 🛠️ Limpeza e Diagnóstico de Estações Windows

Ferramenta automática para consolidar rotinas de manutenção em um único executável.

---

## 📋 O que a ferramenta faz

| Etapa | Ação | Detalhe |
|-------|------|---------|
| **1** | Limpeza de temporários | Remove `C:\Windows\Temp`, `%TEMP%` e `C:\Windows\Prefetch` |
| **2** | Reparo do sistema | Executa `sfc /scannow` (verificação de integridade de arquivos) |
| **3** | Verificação de disco | Agenda `chkdsk C: /F` para a próxima reinicialização |
| **4** | Ferramentas de apoio | Abre Gerenciador de Tarefas, Serviços e Limpeza de Disco |

---

## 🚀 Como usar

### Opção A — Executar diretamente o Python
```
python limpeza_diagnostico_windows.py
```
> Se não estiver em modo administrador, o UAC solicitará elevação automaticamente.

### Opção B — Gerar o EXE standalone (requer Python + PyInstaller)

1. Certifique-se que o Python 3.10+ está instalado.
2. Execute o arquivo `build.bat` com duplo clique.
3. O executável será gerado em `dist\LimpezaDiagnosticoWindows.exe`.
4. Distribua apenas o `.exe` — não depende de Python instalado.

**Ou via linha de comando:**
```
pip install pyinstaller
pyinstaller --onefile --console --uac-admin --name "LimpezaDiagnosticoWindows" limpeza_diagnostico_windows.py
```

---

## ⚙️ Flags PyInstaller explicadas

| Flag | Função |
|------|--------|
| `--onefile` | Gera um único `.exe` sem dependências externas |
| `--console` | Mantém a janela do console visível (necessário para ver o progresso) |
| `--uac-admin` | Força solicitação de elevação UAC ao iniciar |
| `--name` | Define o nome do executável gerado |

---

## ⏱️ Tempo estimado de execução

| Etapa | Tempo aproximado |
|-------|-----------------|
| Limpeza de temporários | 10–60 segundos |
| SFC /scannow | **3–15 minutos** (varia com o disco) |
| Agendamento CHKDSK | Segundos |
| Abertura das ferramentas | Instantâneo |

---

## ⚠️ Notas importantes

- **Reinicie** o computador após a execução para que o `chkdsk` seja realizado.
- Arquivos temporários **em uso** são ignorados sem travar o script.
- O log do SFC fica em `C:\Windows\Logs\CBS\CBS.log`.
- Testado em Windows 10 e Windows 11.

---

## 🔧 Requisitos de desenvolvimento

- Python 3.10 ou superior
- PyInstaller (`pip install pyinstaller`)
- Sistema operacional: Windows 10 / 11

---

## 📁 Estrutura dos arquivos

```
📦 limpeza-diagnostico-windows/
├── limpeza_diagnostico_windows.py   ← Script principal
├── build.bat                        ← Script de compilação (PyInstaller)
└── README.md                        ← Este arquivo
```

Após o build:
```
📦 dist/
└── LimpezaDiagnosticoWindows.exe    ← Executável standalone
```
