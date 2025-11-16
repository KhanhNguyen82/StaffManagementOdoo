# Module: Import CV PDF file
### Technical name: import_pdf_cv

## Overview

This module automatically extracts candidate information (name, email, phone, etc.) from uploaded PDF CV files using OpenAI API, and creates or updates candidate records in Odoo 18.

## Features

- Upload single or multiple CV PDF files directly.
- Upload zip or rar files containing multiple CVs
- Extract structured data (name, phone, email, etc.) using OpenAI.
- Cron job for periodic duplicate cleanup.

---

## 🧠 Requirements

- Odoo 18 CE
- Python 3.10+
- Unrar and p7zip library packages used in Ubuntu/Debian:
  ```bash
  sudo apt-get install unrar p7zip-full p7zip-rar
  ```
- Installed Python dependencies:
  ```bash
  pip install openai PyPDF2
  ```

---

## ⚙️ Configuration

### Setup OpenAI API Key

You need to register an account at [OpenAI](https://platform.openai.com/signup)  (https://platform.openai.com/signup) and create an API key at [OpenAI API Keys](https://platform.openai.com/account/api-keys) (https://platform.openai.com/account/api-keys).

Fill up your OpenAI API in model candidate_import_wizard.py (line #37) code:

```bash
#Example:
OPENAI_API_KEY = "sk-proj-5qq31-hezWQw25MrT9E9g8cWI0NlNh8IX4G-Itcr4WSigQfBa3OfJ56NcIqRJqI"
BASE_URL = "https://api.openai.com/v1/"
```
BASE_URL is OpenAI API endpoint and usually does not need to be changed.


#### Tips:  OpenAI API Key management:
- Create OpenAI API Key: goto https://platform.openai.com/account/api-keys, click [Create new secret key] button (top-right), set name for key, select project for key. If you have not project, you can create a new project. After that you can copy the API key.
- How to paid to OpenAI:
  - Go to https://platform.openai.com/account/billing/overview, click [Add payment method] button, fill up your credit card information to add payment method.
  - After that you can add funds to your OpenAI account, minimum is $5.
  - When you use OpenAI API, your usage fee will be deducted from your account balance.
  - Monitor your usage at https://platform.openai.com/account/billing/usage
---

## 🚀 Deployment

### Option 1: Deploy on Ubuntu (Native)

1. **Copy the module** into your Odoo addons directory:

   ```bash
   #Example:
   cp -r import_pdf_cv /opt/odoo/addons/
   ```

2. **Update the Odoo configuration** to include the module path:

   ```ini
   addons_path = /opt/odoo/odoo-server/addons,/opt/odoo/addons
   ```

3. **Restart the Odoo service:**

   ```bash
   sudo systemctl restart odoo
   ```

4. **Activate Developer Mode** → **Apps** → **Update Apps List** → search for *Import PDF CV* → **Install**.

5. Ensure the environment variable `OPENAI_API_KEY` is available to the Odoo process.

---

### Option 2: Deploy on Docker

1. Add your OpenAI API key in `docker-compose.yml`:

```yaml
  services:
  db:
    image: postgres:16
    mem_limit: 3g
    environment:
      - POSTGRES_DB=postgres
      - POSTGRES_USER=odoo
      - POSTGRES_PASSWORD=odoo
    volumes:
      - odoo-db-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U odoo -d postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s

  odoo:
    build:
      context: .
      dockerfile: Dockerfile
    image: odoo:18
    depends_on:
      db:
	condition: service_healthy
    ports:
      - "8069:8069"
      - "8072:8072"
    environment:
      - HOST=db
      - USER=odoo
      - PASSWORD=odoo
      - LIMIT_REQUEST=262144000
    volumes:
      - ./addons:/mnt/extra-addons
      - ./odoo.conf:/etc/odoo/odoo.conf
      - ./data:/var/lib/odoo/
    restart: always
volumes:
  odoo-db-data:

 ```
The Docker file should look like this:
```angular2html
FROM odoo:18
USER root
# Cài unrar và p7zip để dùng với rarfile
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        unrar p7zip-full p7zip-rar && \
    rm -rf /var/lib/apt/lists/*
# Quay lại user mặc định 'odoo'
USER odoo
```

2. **Start the stack:**

   ```bash
   docker compose up -d
   ```

3. **Access Odoo:** http://localhost:8069 or yourdomain.com:8069

4. **Install the module** “Import PDF CV” from the Apps menu.

---

## 🔁 Cron Jobs

- **Duplicate Cleanup Job**: runs every 4 hours to remove candidates with the same name, email, or phone.
- **PDF Processing Job**: processes queued attachments automatically.

---

## 🧩 Usage

1. Navigate to **Recruitment → Application →Import PDF CV**.
   1. Import PDF CV
   2. Import Zip CV
   3. Upload Multifile
   4. Upload folder
   5. PDF CV to process (to see pending files)

2. The system will show a notification and process the files asynchronously.
3. Results will appear automatically in the **Candidates** list.
---
## Developer Notes

- The main logic is in `models/candidate_import_wizard.py`.
- Uses OpenAI API to extract structured data from CVs.
- OpenAI Model used: `gpt-3.5-turbo`, you can use others like `gpt-4o` if needed, but that expenses more.
- Limit of tokens per request: 16k tokens.
- One request processes one CV file.
- Handles text extraction from PDF using `PyPDF2`.

---

## 📜 License

This module is licensed under the **OPL-1 License**.

---

## 🧑‍💻 Author

Developed by **Nguyen Quoc Khanh**
