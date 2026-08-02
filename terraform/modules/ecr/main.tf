# 1. Backend ECR Repository
resource "aws_ecr_repository" "backend" {
  name                 = "${lower(var.name_prefix)}-backend"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name = "${var.name_prefix}-backend-ecr"
  }
}

# 2. Frontend ECR Repository
resource "aws_ecr_repository" "frontend" {
  name                 = "${lower(var.name_prefix)}-frontend"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name = "${var.name_prefix}-frontend-ecr"
  }
}
