variable "name_prefix" {
  type        = string
  description = "Prefix for ALB resource names"
}

variable "vpc_id" {
  type        = string
  description = "VPC ID where ALB target group will be registered"
}

variable "public_subnet_ids" {
  type        = list(string)
  description = "List of public subnet IDs for ALB placement"
}

variable "alb_security_group_id" {
  type        = string
  description = "Security group ID attached to ALB"
}
