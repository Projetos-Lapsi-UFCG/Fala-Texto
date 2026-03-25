[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

# Fala-Texto

<div align="center">
  <img width="350" height="2000" alt="Image" src="https://github.com/user-attachments/assets/1d1e4d24-db10-4e1a-8598-04288cc1a91a" />
</div>
O projeto Conversão Fala-Texto apresenta uma tecnologia promissora para o reconhecimento de voz, oferecendo uma solução eficaz para a documentação clínica. Esta tecnologia permite que a validação dos dados possa ocorrer simultaneamente ao preenchimento das informações, permitindo que os profissionais de saúde registrem informações de forma mais rápida e precisa. Essa protótipo visa melhorar a captura de dados médicos, reduzir a carga de trabalho dos profissionais de saúde e aprimorar o  a precisão das informações coletadas nos procedimentos de saúde. 

## Arquitetura da solução 

<img width="1138" height="429" alt="Captura de tela 2025-11-17 093757" src="https://github.com/user-attachments/assets/eb6e47f6-2111-49a2-9824-c5079b3107eb" />

A arquitetura mostra um fluxo modular e linear para conversão fala‑texto orientada à documentação clínica: o microfone captura a fala que é enviada ao processador, onde ocorre o pré‑processamento de sinal (filtragem, redução de ruído e detecção de atividade de voz), depois um algoritmo interpretador (modelo de reconhecimento automático de fala) converte o áudio em texto bruto; esse texto segue para o estágio de tratamento de texto (normalização, pontuação, correção, mapeamento de termos clínicos, validação semântica e aplicação de regras de negócio) e, após validação em tempo real, é automaticamente populado nos campos do formulário, com possibilidade de feedback ao usuário e controles de segurança/privacidade.

## Desenvolvimento de App android 

O desenvolvimento de aplicativos Android no contexto da saúde apresenta uma oportunidade valiosa para transformar a maneira como serviços médicos e informações são acessados e gerenciados. Pensando nisso, o app traz para o cotidiano do ambiente hospitalar acessibilidade, inovação tecnológica e eficiência no preenchimento de documentos. Para o desenvolvimento deste aplicativo móvel foram adotadas duas frentes: o framework Kivy (Python) e o Android Studio (Kotlin); ambas apresentam vantagens e limitações, que serão detalhadas a seguir.

### Kivy
-  Kivy é um framework open‑source em Python para criar aplicações gráficas multiplataforma (Windows, macOS, Linux, iOS, Android e Raspberry Pi) com foco em interfaces touch e interativas; ele usa aceleração por GPU e fornece uma biblioteca rica de widgets e suporte a      gestos. A vantagem principal é desenvolver em Python com uma única base de código e empacotar para Android usando ferramentas como python-for-android ou Buildozer, o que facilita prototipagem rápida e integração com bibliotecas Python de ML/ASR já existentes. Em         contrapartida, apps Kivy tendem a ter aparência menos “nativa” e podem exigir ajustes de performance/UX para igualar apps escritos em Kotlin; o empacotamento e acesso a APIs nativas são possíveis, mas adicionam complexidade ao pipeline de build e manutenção.
-  Veja a documentação oficial: [Kivy](https://kivy.org).

### Android Studio
-  Android Studio é o IDE oficial para desenvolvimento Android, baseado no IntelliJ IDEA, oferecendo um fluxo completo: editor com autocompletar e refatoração, sistema de build Gradle, emulador rápido, ferramentas de profiling e integração com Play Store para empacotamento e assinatura. Kotlin é a linguagem recomendada para Android: é moderna, concisa, com sistema de nulidade que reduz NullPointerExceptions e integra-se nativamente com bibliotecas Android; além disso, Jetpack Compose (toolkit declarativo de UI) foi projetado para Kotlin, simplificando a construção de interfaces reativas e adaptativas. Para projetos clínicos ou de produção, o stack Android Studio + Kotlin oferece melhor desempenho nativo, acesso direto a APIs do sistema (microfone, sensores, segurança) e ferramentas de teste/CI integradas, tornando-o a escolha natural quando se precisa de máxima compatibilidade, segurança e experiência de usuário nativa.
-  Veja a documentação oficial: [Android Studio](https://developer.android.com/studio?hl=pt-br).

Após testes em ambientes hospitalares, a combinação Android Studio + Kotlin apresentou os melhores resultados e tornou‑se a solução preferencial quando se busca UI nativa, desempenho máximo, integração profunda com o sistema e suporte corporativo de longo prazo. Essa abordagem proporciona acesso direto às APIs do Android, ferramentas oficiais de profiling, recursos de teste e pipelines de CI/CD, além de Jetpack Compose para interfaces reativas e Kotlin para um código mais conciso e seguro, facilitando a manutenção, as atualizações e a conformidade com requisitos de segurança e privacidade em contextos clínicos.


Organização do código:

```                                                                                                         
  app/
  ├── __init__.py          — create_app() factory       
  ├── config.py            — all settings (JWT, CORS, folders, thresholds) 
  ├── dependencies.py      — limiter, pwd_context,usuarios
  ├── exceptions.py        — rate_limit_handler, authjwt_exception_handler
  ├── models.py            — LoginModel 
  ├── services/
  │   ├── audio_service.py — Whisper + preprocessing + quality metrics
  │   ├── pdf_service.py   — PyMuPDF operations
  │   ├── face_service.py  — DeepFace verification + validation
  │   └── field_mapping.py — 50-condition CSV→PDF mapping (extracted pure functions)
  └── routers/
  ├── auth.py          — GET /, POST /login
  ├── audio.py         — POST /transcricao
  ├── face.py          — POST /autenticacao, /upload-imagem
  └── pdf.py           — POST /listar-campos, /preencher-campos, /imagem, /preencher-pdf
```
