# 1. ECS Fargate Cluster
resource "aws_ecs_cluster" "main" {
  name = "sentellent-cluster"

  tags = {
    Name = "sentellent-cluster"
  }
}

# 2. ECS Task Definition for FastAPI Backend
resource "aws_ecs_task_definition" "backend" {
  family                   = "${var.name_prefix}-backend-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.cpu
  memory                   = var.memory
  execution_role_arn       = var.execution_role_arn
  task_role_arn            = var.task_role_arn

  container_definitions = jsonencode([
    {
      name      = "backend"
      image     = var.backend_image != "" ? var.backend_image : "public.ecr.aws/docker/library/python:3.11-slim"
      essential = true

      portMappings = [
        {
          containerPort = 8000
          hostPort      = 8000
          protocol      = "tcp"
        }
      ]

      environment = [
        { name = "DATABASE_URL", value = var.database_url },
        { name = "GOOGLE_API_KEY", value = var.google_api_key },
        { name = "OPENROUTER_API_KEY", value = var.openrouter_api_key },
        { name = "GOOGLE_CLIENT_ID", value = var.google_client_id },
        { name = "GOOGLE_CLIENT_SECRET", value = var.google_client_secret },
        { name = "AUTH_SECRET", value = var.auth_secret },
        { name = "ALLOWED_ORIGINS", value = var.allowed_origins }
      ]

      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 15
      }

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = var.log_group_name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "backend"
        }
      }
    }
  ])

  tags = {
    Name = "${var.name_prefix}-backend-task"
  }
}

# 3. ECS Fargate Service
resource "aws_ecs_service" "backend" {
  name                               = "${var.name_prefix}-backend-service"
  cluster                            = aws_ecs_cluster.main.id
  task_definition                    = aws_ecs_task_definition.backend.arn
  desired_count                      = 1
  launch_type                        = "FARGATE"
  deployment_maximum_percent         = 200
  deployment_minimum_healthy_percent = 50

  network_configuration {
    subnets          = var.public_subnet_ids
    security_groups  = [var.ecs_security_group_id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = var.target_group_arn
    container_name   = "backend"
    container_port   = 8000
  }

  tags = {
    Name = "${var.name_prefix}-backend-service"
  }
}
