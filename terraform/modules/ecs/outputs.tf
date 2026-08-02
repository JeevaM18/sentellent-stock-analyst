output "cluster_name" {
  value       = aws_ecs_cluster.main.name
  description = "Name of the ECS Cluster"
}

output "service_name" {
  value       = aws_ecs_service.backend.name
  description = "Name of the backend ECS Service"
}

output "task_definition_arn" {
  value       = aws_ecs_task_definition.backend.arn
  description = "ARN of the backend ECS Task Definition"
}
