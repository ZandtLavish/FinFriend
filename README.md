# FinFriend
*A local financial assistant*

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="public/logo_dark.png">
  <source media="(prefers-color-scheme: light)" srcset="public/logo_light.png">
  <img alt="FinFriend logo" src="public/logo_dark.png">
</picture>

<br>

With access to numerous financial tools and services, ***FinFriend*** is designed to efficiently extract the relevant, ever-changing context of the world and apply it to your personal financial goals. Query your LLM without thinking twice about the personal data you're feeding it.

---

# Setup

#### 1. Start Ollama
The Project is designed to run Ollama on the host machine (faster than inside a container). Start the service before running the docker project:

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
Make sure your model supports **"tools"** (see [ollama.com/search](https://ollama.com/search))
***NOTE** – The quality and accuracy of your chat interaction greatly depends on the quality of your model. I found ***qwen3.6*** effective with the tool interactions.*

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