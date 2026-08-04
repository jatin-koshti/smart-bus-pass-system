# Cloud Deployment & Scalability Architecture Guide

This document provides production deployment architectures for **CodeAlpha Task 3: Cloud-Based Smart Bus Pass & Ticket Booking System**.

---

## 1. Cloud Architecture Overview

The system is designed following **12-Factor Cloud-Native Application Principles**:
1. **Stateless Web Tier**: Flask session data and user states are handled via JWT/signed session cookies and database sessions, allowing horizontal auto-scaling.
2. **Managed Relational Storage**: Dual support for SQLite (Local Development) and PostgreSQL (Production Managed Database like AWS RDS, Azure Database for PostgreSQL, GCP Cloud SQL).
3. **Containerization**: Single Docker container artifact with multi-stage Gunicorn WSGI server.
4. **Environment Configuration**: Decoupled environment variables injected via secrets manager or container environment configs.

```
                  ┌─────────────────────────────────┐
                  │   Client Browser / Mobile App   │
                  └────────────────┬────────────────┘
                                   │ HTTPS (443)
                                   ▼
                  ┌─────────────────────────────────┐
                  │      Cloud Load Balancer        │
                  │ (AWS ALB / GCP Cloud LB / Azure)│
                  └────────────────┬────────────────┘
                                   │
                ┌──────────────────┴──────────────────┐
                ▼                                     ▼
     ┌─────────────────────┐               ┌─────────────────────┐
     │ App Instance 1 (WSGI)│               │ App Instance N (WSGI)│
     └──────────┬──────────┘               └──────────┬──────────┘
                │                                     │
                └──────────────────┬──────────────────┘
                                   │ Database Connection Pool
                                   ▼
                  ┌─────────────────────────────────┐
                  │    Managed PostgreSQL DB        │
                  │ (AWS RDS / GCP Cloud SQL / Azure)│
                  └─────────────────────────────────┘
```

---

## 2. Option A: AWS Deployment (App Runner / EC2 + RDS)

### Using AWS App Runner (Serverless Container Deployment)
1. **Push Container to AWS ECR**:
   ```bash
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com
   docker build -t smart-bus-pass .
   docker tag smart-bus-pass:latest <AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/smart-bus-pass:latest
   docker push <AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/smart-bus-pass:latest
   ```

2. **Provision AWS RDS PostgreSQL**:
   - Instance class: `db.t4g.micro` (Free tier eligible).
   - Database name: `smart_bus_db`.
   - Obtain Endpoint URI: `postgresql://bus_admin:PASSWORD@bus-db.xxxx.us-east-1.rds.amazonaws.com:5432/smart_bus_db`.

3. **Deploy App Runner Service**:
   - Select ECR image `<AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/smart-bus-pass:latest`.
   - Environment variables:
     - `DATABASE_URL`: RDS Connection String
     - `SECRET_KEY`: High-entropy secret key
     - `PORT`: `5000`
   - Enable Auto-scaling (Min: 1 instance, Max: 10 instances based on CPU utilization > 70%).

---

## 3. Option B: Azure App Service Deployment

1. **Create Azure Container Registry (ACR) & Push**:
   ```bash
   az acr create --resource-group SmartBusRG --name smartbusacr --sku Basic
   az acr login --name smartbusacr
   docker tag smart-bus-pass:latest smartbusacr.azurecr.io/smart-bus-pass:v1
   docker push smartbusacr.azurecr.io/smart-bus-pass:v1
   ```

2. **Create Azure Database for PostgreSQL Flexible Server**:
   ```bash
   az postgres flexible-server create --resource-group SmartBusRG --name smartbus-postgres-db --admin-user busadmin --admin-password SecurePassword123!
   ```

3. **Deploy App Service for Containers**:
   ```bash
   az webapp create --resource-group SmartBusRG --plan SmartBusPlan --name smartbus-app --deployment-container-image-name smartbusacr.azurecr.io/smart-bus-pass:v1
   az webapp config appsettings set --resource-group SmartBusRG --name smartbus-app --settings DATABASE_URL="postgresql://busadmin:SecurePassword123!@smartbus-postgres-db.postgres.database.azure.com:5432/smart_bus_db" SECRET_KEY="ProductionSecret"
   ```

---

## 4. Option C: Google Cloud Run Deployment

1. **Build and Submit Container to Google Artifact Registry**:
   ```bash
   gcloud auth configure-docker
   gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/smart-bus-pass:latest
   ```

2. **Deploy to Cloud Run with Managed Cloud SQL**:
   ```bash
   gcloud run deploy smart-bus-pass \
     --image gcr.io/YOUR_PROJECT_ID/smart-bus-pass:latest \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars DATABASE_URL="postgresql://bus_admin:PASSWORD@/smart_bus_db?host=/cloudsql/YOUR_PROJECT_ID:us-central1:bus-db-instance",SECRET_KEY="CloudRunSecretKey"
   ```

---

## 5. Production Scalability & Monitoring Best Practices

- **Load Balancing**: AWS Application Load Balancer / Azure Front Door performs TLS termination and routes traffic across multi-AZ container instances.
- **Auto-Scaling**: Set Horizontal Pod Autoscaler (HPA) or container scaling rules based on CPU/RAM threshold (> 75%) or request rate (> 500 req/sec).
- **Caching**: Integrate Redis/ElastiCache for caching seat layout availability and route lookups during high concurrency rush hours.
- **Monitoring & Logging**:
  - AWS CloudWatch Logs / Azure Monitor / GCP Cloud Logging.
  - Health checks endpoint `/api/v1/routes` for load balancer ping checks every 15 seconds.
