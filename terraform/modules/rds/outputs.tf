output "endpoint" {
  value       = aws_db_instance.postgres.endpoint
  description = "The connection endpoint of the PostgreSQL RDS instance"
}

output "address" {
  value       = aws_db_instance.postgres.address
  description = "The hostname address of the PostgreSQL RDS instance"
}

output "port" {
  value       = aws_db_instance.postgres.port
  description = "The port PostgreSQL is listening on"
}

output "database_url" {
  value       = "postgresql+psycopg://${var.db_username}:${var.db_password}@${aws_db_instance.postgres.endpoint}/${var.db_name}"
  description = "Full SQLAlchemy Connection String"
  sensitive   = true
}
