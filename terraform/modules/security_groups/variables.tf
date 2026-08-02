variable "name_prefix" {
  type        = string
  description = "Prefix for security group names"
}

variable "vpc_id" {
  type        = string
  description = "VPC ID where security groups will be created"
}
