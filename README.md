# Chatbot SaaS Platform

## Overview
A complete **SaaS platform** for managing AI-powered Chatbots.  
This platform provides an integrated management system for **companies, users, and websites**, built with **FastAPI**, **PostgreSQL**, and **Docker**.

---

## Tech Stack
- **Backend:** FastAPI (Python 3.10+)
- **Database:** PostgreSQL (Dockerized)
- **ORM:** SQLAlchemy + Alembic
- **Auth:** JWT-based Authentication
- **Containerization:** Docker & Docker Compose

---

## Prerequisites
Before you start, make sure you have installed:
- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

> You don’t need to install PostgreSQL or Redis manually — everything runs in Docker.

---

## Virtual Environment Setup

### Windows
```bash
python -m venv venv
venv\Scripts\activate
Linux / Mac
bash
Copy code
python3 -m venv venv
source venv/bin/activate
Install required dependencies:

bash
Copy code
pip install -r requirements.txt
Run the Platform using Docker
bash
Copy code
cd docker
docker-compose up --build
This will:

Start PostgreSQL database

Start FastAPI backend

Automatically apply environment variables

Initialize the Database
After containers are running:

bash
Copy code
alembic upgrade head
python -m app.core.init_db
This creates:

Superadmin account

Default subscription plans

Demo company & master user

Run Development Server
bash
Copy code
uvicorn app.main:app --reload
Access the Application
Resource	URL
Swagger Docs	http://localhost:8000/docs
Redoc	http://localhost:8000/redoc
Health Check	http://localhost:8000/health

Default Accounts
Role	Email	Password
Superadmin	admin@chatbot-saas.com	changeme123
Demo User	demo@chatbot-saas.com	demo123

yaml
Copy code
