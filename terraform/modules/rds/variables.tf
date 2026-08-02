variable "name_prefix" {
  type        = string
  description = "Prefix for RDS resource names"
}

variable "private_subnet_ids" {
  type        = list(string)
  description = "Private subnet IDs for DB Subnet Group"
}

variable "rds_security_group_id" {
  type        = string
  description = "Security group ID attached to RDS"
}

variable "db_name" {
  type        = string
  description = "Name of initial PostgreSQL database"
}

variable "db_username" {
  type        = string
  description = "Admin username for PostgreSQL"
}

variable "db_password" {
  type        = string
  description = "Admin password for PostgreSQL"
  sensitive   = true
}
