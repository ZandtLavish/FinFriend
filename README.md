# FinFriend
*A local financial assistant*

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="public/logo_dark.png">
  <source media="(prefers-color-scheme: light)" srcset="public/logo_light.png">
  <img alt="FinFriend logo" src="public/logo_dark.png">
</picture>

<br>

With access to numerous tools and services, ***FinFriend*** is designed to efficiently extract the relevant, ever-changing context of the financial world and apply it to your personal financial goals. Query your agent without thinking twice about the sensitive information you're providing it.

---

# Current Integrations

- **FRED**
- **Yahoo Finance**
- **SEC Filings**

---

# Setup

#### 1. Start Ollama
***FinFriend*** is designed to run Ollama on the host machine (this is notably faster than inside a container). Start the service before running the docker project:

**MacOS**
```bash
ollama serve
```

**Linux**
```bash
systemctl start ollama
systemctl status ollama
```

#### 2. Download Model & Embeddings
Considerations when choosing a model (see [ollama.com/search](https://ollama.com/search))
- Make sure your model supports **"tools"**
- The quality and accuracy of your chat interaction greatly depends on the quality of your model. I find `qwen3.6` effective with the tool interactions.

```bash
ollama pull nomic-embed-text
ollama pull [ qwen3.6 | mistral-nemo | ... ]
```

#### 3. Run Docker Project
```bash
cd <project>
docker compose build
docker compose up
```

#### 4. Set Environment Variables
You need to set a few key environment variables to get everything connected. Create a `.env` file in the same directory as the `Dockerfile` and note the following variables you'll set:
```
LLM_MODEL
CHROMA_TOKEN
FRED_KEY
SEC_EMAIL # Required by SEC
```

To Create your Chroma secret run the following in your terminal to generate a random secret for your **Chroma Host** (keep it secret, keep it safe):
```bash
openssl rand -hex 32
```
...and set it as the `CHROMA_TOKEN` environment variable (in your `.env` file)
```bash
CHROMA_TOKEN="1234abcd..."
```

**NOTE** - You can also edit the variables under the `app/config.py:Settings` class variables. However, the project assumes a `.env` file will be present when building the container

---

# Getting Started

1. Build and launch the Docker project
```bash
docker compose build
docker compose up
```

2. Visit the local Chainlit site using your favorite browser:
```bash
http://0.0.0.0:8000
```