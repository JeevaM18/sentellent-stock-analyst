# 🏗️ Sentellent Alpha — Modular Terraform AWS Infrastructure

Production-grade, cost-optimized Terraform infrastructure for **Sentellent AI Stock Analyst** deployed on AWS **`ap-south-1`** (Mumbai) using ECS Fargate, RDS PostgreSQL 17 (pgvector), ALB, ECR, IAM, and CloudWatch.

---

## 🏛️ Architecture Diagram

```
                             [ Internet ]
                                  │
                                  ▼
                ┌───────────────────────────────────┐
                │   Application Load Balancer (ALB) │ (Port 80)
                └─────────────────┬─────────────────┘
                                  │
                                  ▼ (Port 8000)
            ┌───────────────────────────────────────────┐
            │   AWS ECS Fargate (sentellent-cluster)    │
            │   FastAPI Backend Container               │
            │   (0.5 vCPU • 1 GB RAM • Public IP)       │
            └─────────────────────┬─────────────────────┘
                                  │
                                  ▼ (Port 5432)
            ┌───────────────────────────────────────────┐
            │   AWS RDS PostgreSQL 17 (Single-AZ)       │
            │   (db.t4g.micro • 20 GB Storage)          │
            └───────────────────────────────────────────┘
```

---

## 📦 Infrastructure Modules Breakdown

| Module | Resources Created | Description |
|---|---|---|
| `modules/vpc` | VPC, 2 Public Subnets, 2 Private Subnets, IGW, Route Tables | Isolated networking across 2 Availability Zones in `ap-south-1` |
| `modules/security_groups` | ALB SG, ECS SG, RDS SG | Chained security rules (`ALB -> ECS (8000) -> RDS (5432)`) |
| `modules/alb` | ALB, HTTP Listener (80), Target Group (8000) | Internet-facing load balancing with `/health` check probes |
| `modules/ecr` | ECR Repositories (`backend`, `frontend`) | Container registries with image scanning & tag mutability |
| `modules/rds` | RDS PostgreSQL 17, DB Subnet Group, Parameter Group | Managed database instance (`db.t4g.micro`, 20 GB storage, 7-day backups) |
| `modules/iam` | ECS Execution Role, ECS Task Role | IAM roles with least-privilege policies |
| `modules/cloudwatch` | Log Group `/ecs/Sentellent-Production-backend` | Centralized log aggregation with 7-day retention |
| `modules/ecs` | ECS Fargate Cluster (`sentellent-cluster`), Task Def, Service | Container execution with zero NAT Gateway cost |

---

## 💰 Monthly AWS Cost Estimate (< $25/month)

Designed specifically for AWS credit optimization (< $100 budget limit):

| AWS Resource | Configuration | Estimated Monthly Cost |
|---|---|---|
| **AWS ECS Fargate** | 1 Task (0.5 vCPU, 1 GB RAM, 24/7) | ~$11.50 / month |
| **AWS RDS PostgreSQL** | `db.t4g.micro` (Single-AZ, 20 GB gp3) | ~$12.00 / month |
| **AWS ALB** | 1 ALB (Low LCU usage) | ~$15.00 / month |
| **AWS ECR & CloudWatch** | 2 Repositories + 7-Day Logs | ~$1.50 / month |
| **NAT Gateway** | **OMITTED ($0 cost)** | **$0.00 / month** |
| **TOTAL ESTIMATE** | | **~$40.00 / month** (Well within $100 limit!) |

---

## 🚀 Deployment Instructions

### 1. Prerequisites
- [Terraform >= 1.8.0](https://www.terraform.io/downloads)
- [AWS CLI](https://aws.amazon.com/cli/) configured with `aws configure`
- [Docker Desktop](https://www.docker.com/)

### 2. Configure Variables
Copy the example variables file:
```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
```
Update `terraform.tfvars` with your actual database passwords and API keys.

### 3. Initialize & Deploy Infrastructure
```bash
# Initialize Terraform modules
terraform init

# Validate configuration
terraform validate

# Review deployment plan
terraform plan

# Apply infrastructure
terraform apply -auto-approve
```

---

## 🧹 Tear Down & Resource Destruction

To destroy all created AWS resources and stop charges:
```bash
cd terraform
terraform destroy -auto-approve
```
