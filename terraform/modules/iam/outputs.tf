output "execution_role_arn" {
  value       = aws_iam_role.ecs_execution.arn
  description = "ARN of the ECS Task Execution Role"
}

output "task_role_arn" {
  value       = aws_iam_role.ecs_task.arn
  description = "ARN of the ECS Task Role"
}
