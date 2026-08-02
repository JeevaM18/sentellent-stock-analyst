resource "aws_cloudwatch_log_group" "backend" {
  name              = "/ecs/${var.name_prefix}-backend"
  retention_in_days = var.retention_in_days

  tags = {
    Name = "${var.name_prefix}-backend-logs"
  }
}
