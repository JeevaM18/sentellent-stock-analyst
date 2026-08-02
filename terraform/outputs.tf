output "alb_dns_name" {
  description = "Public URL DNS of the Application Load Balancer"
  value       = module.alb.alb_dns_name
}

output "rds_endpoint" {
  description = "Connection endpoint of PostgreSQL RDS"
  value       = module.rds.endpoint
}

output "ecs_cluster_name" {
  description = "Name of the ECS Cluster"
  value       = module.ecs.cluster_name
}

output "ecs_service_name" {
  description = "Name of the backend ECS Service"
  value       = module.ecs.service_name
}

output "ecr_backend_repository_url" {
  description = "ECR Backend Image Repository URI"
  value       = module.ecr.backend_repository_url
}

output "ecr_frontend_repository_url" {
  description = "ECR Frontend Image Repository URI"
  value       = module.ecr.frontend_repository_url
}
