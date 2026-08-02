output "alb_dns_name" {
  value       = aws_lb.main.dns_name
  description = "The public DNS name of the Application Load Balancer"
}

output "alb_arn" {
  value       = aws_lb.main.arn
  description = "ARN of the Application Load Balancer"
}

output "target_group_arn" {
  value       = aws_lb_target_group.backend.arn
  description = "ARN of the backend target group"
}
