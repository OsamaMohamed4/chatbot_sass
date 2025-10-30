# 🤖 Chatbot SaaS Platform

## 📋 Overview
A complete **SaaS platform** for managing AI-powered Chatbots.  
This platform provides an integrated management system for **companies, users, and websites**, built with **FastAPI**, **PostgreSQL**, and **Docker**.

---

## 🚀 Tech Stack
- **Backend:** FastAPI (Python 3.10+)
- **Database:** PostgreSQL (Dockerized)
- **ORM:** SQLAlchemy + Alembic
- **Auth:** JWT-based Authentication
- **Containerization:** Docker & Docker Compose


---

## 🧱 Prerequisites
Before you start, make sure you have installed:
- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

> 💡 You don’t need to install PostgreSQL or Redis manually — everything runs in Docker.

---

## ⚙️ Setup & Installation

### 1️⃣ Clone the Repository
```bash
git clone <repository-url>
cd chatbot-saas-platform
2️⃣ Create .env File
Create a .env file in the root directory with this minimal config:

ini
Copy code
PROJECT_NAME=Chatbot SaaS Platform
POSTGRES_USER=chatbot_user
POSTGRES_PASSWORD=chatbot_pass
POSTGRES_DB=chatbot_saas
SECRET_KEY=supersecretkey
ACCESS_TOKEN_EXPIRE_MINUTES=1440
3️⃣ Run the Platform using Docker
bash
Copy code
cd docker
docker-compose up --build
This will:

Start PostgreSQL database

Start FastAPI backend

Automatically apply environment variables

4️⃣ Initialize the Database
After containers are running:

bash
Copy code
alembic upgrade head
python -m app.core.init_db
This creates:
✅ Superadmin account
✅ Default subscription plans
✅ Demo company & master user

uvicorn app.main:app --reload

5️⃣ Access the Application
Resource	URL
Swagger Docs	http://localhost:8000/docs
Redoc	http://localhost:8000/redoc
Health Check	http://localhost:8000/health

🔑 Default Accounts
Role	Email	Password
Superadmin	admin@chatbot-saas.com	changeme123
Demo User	demo@chatbot-saas.com	demo123

