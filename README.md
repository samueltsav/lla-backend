## Project Name
LinguAfrika

## Overview
LinguAfrika is an AI-powered language learning application, built with a focus on African languages. The MVP targets Hausa, Yoruba, Igbo, Swahili and Wolof.

## Tech Stack
- Python
- Django
- PostgreSQL
- MongoDB
- Celery + Redis + RabbitMQ
- Docker
- Jira
- confluence
- Microsoft Teams

## Architecture
- Microservices
- Services communicate via an API gateway while all async communications are via Celery

## Key Features
- Authentication (Clerk/JWT)
- Background tasks 
- Role-based access
- API documentation

## How to Run Locally
- Have Docker installed and running
- Clone the repo
- Run the command: docker compose up --build -d (This spins up all the containers)
- Access the Swagger-ui documentation at 127.0.0.1:8001/auth/schema/docs (user_service) and 127.0.0.1:8002/api/schema/docs (content_service)

## What I Learned on this project
- Ways of working in a cross-functional team
- Project architecture design and documentation
- Hands-on experience with the microservices architecture

