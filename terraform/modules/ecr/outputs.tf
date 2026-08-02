output "backend_repository_url" {
  value       = aws_ecr_repository.backend.repository_url
  description = "ECR Repository URL for Backend image"
}

output "frontend_repository_url" {
  value       = aws_ecr_repository.frontend.repository_url
  description = "ECR Repository URL for Frontend image"
}
