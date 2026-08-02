variable "name_prefix" {
  type        = string
  description = "Prefix for CloudWatch resource names"
}

variable "retention_in_days" {
  type        = number
  description = "CloudWatch log retention in days"
  default     = 7
}
