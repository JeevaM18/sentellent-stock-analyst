variable "name_prefix" {
  type        = string
  description = "Prefix for ECS cluster and service names"
}

variable "aws_region" {
  type        = string
  description = "AWS Region"
}

variable "public_subnet_ids" {
  type        = list(string)
  description = "Public subnet IDs for ECS task deployment (No NAT Gateway cost)"
}

variable "ecs_security_group_id" {
  type        = string
  description = "Security group ID attached to ECS task"
}

variable "target_group_arn" {
  type        = string
  description = "ARN of ALB target group"
}

variable "execution_role_arn" {
  type        = string
  description = "ARN of IAM Execution Role"
}

variable "task_role_arn" {
  type        = string
  description = "ARN of IAM Task Role"
}

variable "log_group_name" {
  type        = string
  description = "Name of CloudWatch log group"
}

variable "backend_image" {
  type        = string
  description = "ECR Image URI for Backend container"
}

variable "cpu" {
  type        = number
  description = "CPU units (512 = 0.5 vCPU)"
  default     = 512
}

variable "memory" {
  type        = number
  description = "Memory in MB (1024 = 1 GB)"
  default     = 1024
}

variable "database_url" {
  type        = string
  description = "PostgreSQL DATABASE_URL string"
  sensitive   = true
}

variable "google_api_key" {
  type        = string
  description = "Google Gemini API Key"
  sensitive   = true
}

variable "openrouter_api_key" {
  type        = string
  description = "OpenRouter API Key"
  sensitive   = true
}

variable "google_client_id" {
  type        = string
  description = "Google OAuth Client ID"
}

variable "google_client_secret" {
  type        = string
  description = "Google OAuth Client Secret"
  sensitive   = true
}

variable "auth_secret" {
  type        = string
  description = "JWT / Auth Session Secret"
  sensitive   = true
}

variable "allowed_origins" {
  type        = string
  description = "CORS Allowed Origins"
}
