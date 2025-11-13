# 🔐 Sistema de Reconhecimento Facial com MFA

**Projeto Acadêmico - Universidade Paulista (UNIP)**  
**Curso:** Ciência da Computação - Sexto Semestre  
**Disciplina:** Processamento de Imagem e Visão Computacional (PIVC)  

---

## 👥 Autores
- **G8694J8** Isabela Cicilio de Andrade  
- **N20HJ4** Raphael Della Torre Gimenes  
- **G763289** Giovanne Monti Guedes Morgado  

---

## 🧠 Descrição do Projeto

Este projeto foi desenvolvido para atender as especificações do projeto de APS (Atividade Prática Supervisionada).  
O sistema implementa um **mecanismo de autenticação biométrica** baseado em **reconhecimento facial** com suporte a **autenticação multifator (MFA)**.  

Desenvolvido com **redes neurais (OpenCV DNN + FaceNet)**, oferece três níveis de segurança configuráveis, **criptografia AES-256** para proteção de dados sensíveis e um **sistema de auditoria imutável estilo blockchain**.

---

## ✨ Funcionalidades Principais

- **🎯 Reconhecimento Facial de Alta Precisão** — Usa SSD ResNet e FaceNet com embeddings de 128 dimensões.  
- **🔒 Três Níveis de Segurança Configuráveis**
  - **Nível 1:** Reconhecimento facial básico (`threshold: 0.65–0.75`)
  - **Nível 2:** Facial + MFA obrigatório (`threshold: 0.75–0.85`)
  - **Nível 3:** Máxima segurança com MFA (`threshold: 0.80–0.90`)
- **📱 Autenticação Multifator (MFA/2FA)** — Integração com Google Authenticator (TOTP).  
- **🔐 Criptografia End-to-End** — AES-256 (Fernet) para proteger embeddings e secrets.  
- **📋 Sistema de Auditoria Imutável** — Logs com hash SHA-256 encadeados.  
- **🛡️ Proteção contra Força Bruta** — Lockout automático de 5 minutos após 3 falhas.

---

## 📸 Capturas de Tela

| Tela | Imagem |
|------|---------|
| **Tela Inicial** | ![Tela Inicial](https://i.imgur.com/00lyZvt.png) |
| **Cadastro de Usuário** | ![Cadastro](https://i.imgur.com/37xhfiD.png) |
| **Login com Reconhecimento Facial** | ![Login](https://i.imgur.com/NsSfTeg.png) |
| **Gestão de Usuários** | ![Gestão](https://i.imgur.com/3nBRDaM.png) |
| **Configurações de Segurança** | ![Configurações](https://i.imgur.com/T4sBW5I.png) |
| **Auditoria e Logs** | ![Auditoria](https://i.imgur.com/h8zW06z.png) |

---

## 🎥 Demonstração em Vídeo

📺 **[Assista no YouTube](https://www.youtube.com/watch?v=X9AlspBXXvE&feature=youtu.be)**

---

## ⚙️ Tecnologias Utilizadas

### Backend
- Python 3.13  
- Flask  
- OpenCV  
- NumPy  
- Cryptography (AES-256)  
- PyOTP  
- QRCode  

### Frontend
- HTML5 / CSS3  
- JavaScript  
- MediaDevices API

### Modelos de Deep Learning
- **SSD ResNet** — detecção facial  
- **FaceNet** — extração de embeddings 128D

---

## 🚀 Instalação

### Requisitos
- Python 3.8+  
- Webcam (640x480+)  
- Navegador moderno (Chrome, Firefox, Edge)  
- 4GB RAM (8GB recomendado)  
- 500MB livres para modelos

### Passos de Cadastro
1. Acesse a página inicial e clique em **Cadastrar**.  
2. Escolha o **nível de segurança**.  
3. Capture sua foto ou envie uma imagem.  
4. Configure o **MFA** (Google Authenticator) se aplicável.  

---

## 🔬 Arquitetura Técnica

### Fluxo de Cadastro
1. Captura e envio da imagem via API.  
2. OpenCV detecta o rosto (SSD ResNet).  
3. FaceNet gera embeddings de 128D.  
4. Dados criptografados com AES-256.  
5. MFA configurado com PyOTP.  
6. Registro de auditoria com hash SHA-256.

### Fluxo de Autenticação
1. Captura contínua via webcam.  
2. Extração de embeddings e comparação com base local.  
3. Validação de threshold e código MFA.  
4. Lockout após 3 falhas.

---

## 🔐 Segurança e Auditoria

- Embeddings e MFA secrets criptografados (AES-256).  
- Cadeia de logs com SHA-256 (estilo blockchain).  
- Lockout de 5 minutos após 3 falhas.  
- Thresholds ajustáveis.  
- CORS configurado.  

---

## 🌐 Endpoints Principais

| Categoria | Endpoint | Descrição |
|------------|-----------|-----------|
| **Auth** | `POST /api/auth/enroll` | Cadastrar usuário |
|  | `POST /api/auth/authenticate` | Autenticar facialmente |
|  | `POST /api/auth/verify-mfa` | Validar MFA |
| **Usuários** | `GET /api/users` | Listar usuários |
|  | `GET /api/users/<username>` | Obter usuário |
|  | `DELETE /api/users/<username>` | Remover usuário |
| **Configuração** | `GET /api/config` | Obter thresholds |
|  | `PUT /api/config` | Atualizar thresholds |
| **Auditoria** | `GET /api/audit/logs` | Obter logs |
|  | `POST /api/audit/verify-integrity` | Verificar integridade |
| **Saúde** | `GET /api/health` | Status da API |

---

## 🧩 Tecnologias-Chave

- **Detecção Facial:** SSD ResNet  
- **Features:** FaceNet (128D embeddings)  
- **Criptografia:** Fernet (AES-256)  
- **MFA:** TOTP (RFC 6238)  
- **Auditoria:** SHA-256 em cadeia

---

© 2025 - Universidade Paulista (UNIP) — Projeto APS - Ciência da Computação
