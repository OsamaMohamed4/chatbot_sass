# Chatbot SaaS Platform – Phase 1

##  Overview
This project is the **first phase** of a scalable SaaS chatbot platform.  
It includes a solid backend foundation with complete authentication, authorization, and DevOps setup ready for production deployment.

---

##  Features Implemented

###  Database & ORM
- **Complete Database Schema** with all relationships between entities.  
- Managed and versioned using **Alembic** for smooth database migrations.  
- PostgreSQL used as the main relational database.

---

###  Authentication & Authorization
- **JWT Authentication** with access and refresh tokens.  
- **Password hashing** using bcrypt.  
- **Account lockout** and **failed login tracking** for enhanced security.  
- **Role-Based Access Control (RBAC)** for Admins, Companies, and Users.

---

###  Docker & Deployment
- **Docker setup** ready for both development and production environments.  
- Multi-stage Dockerfile and `docker-compose` configurations for fast local testing and deployment.

---

###  API Endpoints
Core API endpoints implemented for:
- **Admin** – manage users, roles, and configurations.  
- **Companies** – manage chatbot accounts and API usage.

Built with **FastAPI** for high performance and scalability.

---

###  Security Features
- Password hashing & salting  
- JWT token-based authentication  
- Account lockout for failed login attempts  
- CORS protection  
- Input validation and secure exception handling

---

###  Background & Monitoring
- **Celery + Redis** for async/background tasks  
- **Prometheus** for performance metrics  
- **Sentry** for real-time error monitoring

---

###  Tech Stack

| Component | Technology |
|------------|-------------|
| Backend Framework | FastAPI |
| Database | PostgreSQL |
| ORM & Migrations | SQLAlchemy + Alembic |
| Task Queue | Celery + Redis |
| Authentication | JWT (Access & Refresh Tokens) |
| Monitoring | Prometheus, Sentry |
| Containerization | Docker, Docker Compose |
| Language | Python 3.10+ |