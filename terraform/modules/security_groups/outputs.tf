output "alb_security_group_id" {
  value       = aws_security_group.alb.id
  description = "ID of the ALB security group"
}

output "ecs_security_group_id" {
  value       = aws_security_group.ecs.id
  description = "ID of the ECS security group"
}

output "rds_security_group_id" {
  value       = aws_security_group.rds.id
  description = "ID of the RDS security group"
}
