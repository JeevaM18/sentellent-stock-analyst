variable "aws_region" {
  description = "AWS Region for deployment"
  type        = string
  default     = "ap-south-1"
}

variable "project_name" {
  description = "Project name tag and naming prefix"
  type        = string
  default     = "Sentellent"
}

variable "environment" {
  description = "Deployment environment (Production / Staging / Dev)"
  type        = string
  default     = "Production"
}

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "Public subnet CIDR blocks (2 AZs)"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "Private subnet CIDR blocks (2 AZs)"
  type        = list(string)
  default     = ["10.0.10.0/24", "10.0.11.0/24"]
}

variable "db_name" {
  description = "PostgreSQL Database Name"
  type        = string
  default     = "stock_analyst"
}

variable "db_username" {
  description = "PostgreSQL Database Admin Username"
  type        = string
  default     = "jeeva"
}

variable "db_password" {
  description = "PostgreSQL Database Admin Password"
  type        = string
  sensitive   = true
}

variable "backend_image" {
  description = "Full ECR Image URI for Backend container"
  type        = string
  default     = ""
}

variable "cpu" {
  description = "ECS Task CPU allocation (0.5 vCPU = 512)"
  type        = number
  default     = 512
}

variable "memory" {
  description = "ECS Task Memory allocation in MB (1 GB = 1024)"
  type        = number
  default     = 1024
}

variable "google_api_key" {
  description = "Google Gemini API Key"
  type        = string
  sensitive   = true
  default     = ""
}

variable "openrouter_api_key" {
  description = "OpenRouter API Key"
  type        = string
  sensitive   = true
  default     = ""
}

variable "google_client_id" {
  description = "Google OAuth Client ID"
  type        = string
  default     = ""
}

variable "google_client_secret" {
  description = "Google OAuth Client Secret"
  type        = string
  sensitive   = true
  default     = ""
}

variable "auth_secret" {
  description = "JWT / Auth Session Secret"
  type        = string
  sensitive   = true
  default     = "ba33e4914440fff6ceb17f4d868656e11b2cce74de5dd1368bbc8b04ade5bcfb"
}

variable "allowed_origins" {
  description = "CORS Allowed Origins"
  type        = string
  default     = "*"
}
