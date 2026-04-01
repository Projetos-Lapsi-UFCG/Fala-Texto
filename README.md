[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

# Fala-Texto

Sistema de conversão de fala em texto para documentação clínica. Profissionais de saúde gravam informações por voz e o sistema transcreve, valida e preenche automaticamente formulários médicos em PDF.

---

## Sumário

- [Visão Geral](#visão-geral)
- [Arquitetura](#arquitetura)
- [Estrutura do Repositório](#estrutura-do-repositório)
- [Componentes](#componentes)
  - [App Android — Kotlin (principal)](#app-android--kotlin-principal)
  - [Backend FastAPI](#backend-fastapi)
  - [Fine-Tuning do Whisper](#fine-tuning-do-whisper)
  - [App Kivy (legado)](#app-kivy-legado)
- [Instalação do APK (usuário final)](#instalação-do-apk-usuário-final)
- [Licença](#licença)

---

## Visão Geral

<div align="center">
  <img width="350" alt="Fala-Texto App" src="https://github.com/user-attachments/assets/1d1e4d24-db10-4e1a-8598-04288cc1a91a" />
</div>

O Fala-Texto foi desenvolvido para reduzir a carga de trabalho de profissionais de saúde no preenchimento de documentos clínicos. Com ele é possível:

- Gravar informações por voz diretamente no ambiente hospitalar
- Transcrever automaticamente o áudio usando o modelo Whisper
- Validar terminologia clínica em tempo real durante o preenchimento
- Popular campos de formulários PDF sem digitação manual

---

## Arquitetura

<img width="1138" height="429" alt="Arquitetura do sistema" src="https://github.com/user-attachments/assets/eb6e47f6-2111-49a2-9824-c5079b3107eb" />

O fluxo de processamento é modular e linear:

1. **Captura** — microfone do dispositivo Android grava o áudio
2. **Pré-processamento** — filtragem de ruído, redução de interferências e detecção de atividade de voz
3. **Reconhecimento de fala** — modelo Whisper converte o áudio em texto bruto
4. **Tratamento de texto** — normalização, pontuação, correção ortográfica, mapeamento de termos clínicos e validação semântica
5. **Preenchimento** — texto validado é inserido automaticamente nos campos do formulário PDF, com feedback ao usuário e controles de segurança


Arquitetura alto nível da solução:

```mermaid
graph TD
    A[Profissional de Saúde] -->|Voz/Áudio| B(Módulo de Captação)
    B --> C{Motor de Processamento}
    
    subgraph "Núcleo de Inteligência (LAPSI)"
    C -->|Conversão| D[Transcrição de Texto]
    D --> E[Validação de Termos Médicos]
    end
    
    E --> F[Interface de Revisão]
    F -->|Dados Validados| G[(Prontuário Eletrônico)]
    F -->|Sincronização| H[RNDS - Rede Nacional de Dados em Saúde]
    
    style C fill:#949,stroke:#333,stroke-width:2px
    style H fill:#281,stroke:#333,stroke-width:2px
```

## Estrutura do Repositório

| Pasta | Descrição |
|-------|-----------|
| `App-Kotlin/VoiceSurgeryWhisper/` | App Android principal (Kotlin + Retrofit2 + Jetpack) |
| `App-Kotlin/VoiceSurgeryGoogleAPI/` | Versão alternativa usando o SpeechRecognizer nativo do Android |
| `a-transcricao/backend/` | Backend principal (FastAPI + Whisper turbo + GPU) |
| `servico-transcricao/API/` | Backend legado em Flask (mantido como referência) |
| `Fine-Tuning/` | Scripts para fine-tuning do Whisper com dados clínicos em português |
| `App-kivy/` | Protótipo legado em Python/Kivy |
| `Instalação (APK)/` | Guia de instalação do APK para usuários finais |

---

## Componentes

### App Android — Kotlin (principal)

O stack **Android Studio + Kotlin** é a solução preferencial após testes em ambiente hospitalar. Oferece:

- Interface nativa com melhor desempenho e UX
- Acesso direto às APIs do sistema (microfone, segurança)
- Suporte a Jetpack Compose para interfaces reativas
- Ferramentas integradas de profiling, testes e CI/CD

**Como compilar e executar:**

```bash
cd App-Kotlin/VoiceSurgeryWhisper

./gradlew assembleDebug          # Gera APK de debug
./gradlew assembleRelease        # Gera APK de release
./gradlew installDebug           # Instala no dispositivo/emulador conectado
./gradlew test                   # Testes unitários
./gradlew connectedAndroidTest   # Testes instrumentados
```

> Requisitos: minSdk 28, targetSdk 36, Kotlin JVM target 11, heap JVM 2 GB.

---

### Backend FastAPI

O backend recebe o áudio do app, realiza a transcrição com Whisper e devolve o texto normalizado para preenchimento do PDF.

**Execução local:**

```bash
cd servico-transcricao/backend
pip install -r requirements.txt
uvicorn servico:app --host 0.0.0.0 --port 3050
```

**Docker (produção com GPU):**

```bash
docker build -t transcricao-api .
docker run -d -p 3050:3050 --restart always -m 6g --gpus all \
  -v /path/to/volume:/app/imagens transcricao-api
```

**Estrutura do código:**

```
app/
├── __init__.py          — factory create_app()
├── config.py            — configurações (JWT, CORS, pastas, thresholds)
├── dependencies.py      — limiter, pwd_context, usuários
├── exceptions.py        — handlers de rate limit e JWT
├── models.py            — LoginModel
├── services/
│   ├── audio_service.py — Whisper + pré-processamento + métricas de qualidade
│   ├── pdf_service.py   — operações com PyMuPDF
│   ├── face_service.py  — verificação com DeepFace/FaceNet
│   └── field_mapping.py — mapeamento CSV→PDF (50 condições)
└── routers/
    ├── auth.py          — GET /, POST /login
    ├── audio.py         — POST /transcricao
    ├── face.py          — POST /autenticacao, /upload-imagem
    └── pdf.py           — POST /listar-campos, /preencher-campos, /imagem, /preencher-pdf
```

O proxy reverso Nginx está configurado em `servico-transcricao/backend/processarpdffalatex.zapto.org.conf`.

---

### Fine-Tuning do Whisper

Scripts para ajuste fino do modelo Whisper com dados clínicos em português, melhorando a precisão na transcrição de termos médicos.

```bash
cd Fine-Tuning
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

python Transformers.py    # Treina o modelo (requer GPU)
python Avaliarmodelo.py   # Avalia com a métrica WER
```

> Antes de treinar, insira seu token do Hugging Face na função de login do `Transformers.py`.
> Para avaliação, defina `MODEL_PATH` (pasta do modelo treinado) e `AUDIO_FILE_PATH` (arquivos de áudio de teste).

---

### App Kivy (legado)

Protótipo inicial desenvolvido em Python com o framework [Kivy](https://kivy.org), mantido apenas como referência. O build para Android usa o Buildozer:

```bash
cd App-kivy
buildozer init           # Inicializa configuração
buildozer -v android debug    # Gera APK de debug
buildozer -v android release  # Gera APK de release
```

> Limitações: interface menos nativa, maior complexidade de build e acesso limitado a APIs do sistema em comparação com o app Kotlin.

---

## Instalação do APK (usuário final)

Para instalar o app sem passar pela Play Store:

1. Baixe o arquivo `.apk` da pasta `Instalação (APK)/` ou `App-Kotlin/VoiceSurgeryGoogleAPI/apk+pdf/`
2. No GitHub, use o botão **"View Raw"** ou **"Download"** para baixar o arquivo
3. No dispositivo Android, acesse a pasta **Downloads** e toque no arquivo `.apk`
4. Se solicitado, habilite a instalação de **fontes desconhecidas** nas configurações de segurança
5. Confirme a instalação e conceda a permissão de gravação de áudio ao abrir o app pela primeira vez

> O sistema pode exibir um alerta de segurança pois o app é um protótipo e não está publicado na Play Store. Isso é esperado.

---

## Licença

Distribuído sob a licença [Apache 2.0](LICENSE).
>>>>>>> Stashed changes
