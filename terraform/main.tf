data "aws_availability_zones" "available" {
  state = "available"
}

# 1. VPC Module
module "vpc" {
  source = "./modules/vpc"

  name_prefix          = local.name_prefix
  vpc_cidr             = var.vpc_cidr
  public_subnet_cidrs  = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
  availability_zones   = slice(data.aws_availability_zones.available.names, 0, 2)
}

# 2. Security Groups Module
module "security_groups" {
  source = "./modules/security_groups"

  name_prefix = local.name_prefix
  vpc_id      = module.vpc.vpc_id
}

# 3. Application Load Balancer Module
module "alb" {
  source = "./modules/alb"

  name_prefix           = local.name_prefix
  vpc_id                = module.vpc.vpc_id
  public_subnet_ids     = module.vpc.public_subnet_ids
  alb_security_group_id = module.security_groups.alb_security_group_id
}

# 4. Amazon ECR Repositories Module
module "ecr" {
  source = "./modules/ecr"

  name_prefix = local.name_prefix
}

# 5. Amazon RDS PostgreSQL Module
module "rds" {
  source = "./modules/rds"

  name_prefix           = local.name_prefix
  private_subnet_ids    = module.vpc.private_subnet_ids
  rds_security_group_id = module.security_groups.rds_security_group_id
  db_name               = var.db_name
  db_username           = var.db_username
  db_password           = var.db_password
}

# 6. IAM Roles Module
module "iam" {
  source = "./modules/iam"

  name_prefix = local.name_prefix
}

# 7. CloudWatch Logs Module
module "cloudwatch" {
  source = "./modules/cloudwatch"

  name_prefix       = local.name_prefix
  retention_in_days = 7
}

# 8. Amazon ECS Fargate Module
module "ecs" {
  source = "./modules/ecs"

  name_prefix           = local.name_prefix
  aws_region            = var.aws_region
  public_subnet_ids     = module.vpc.public_subnet_ids
  ecs_security_group_id = module.security_groups.ecs_security_group_id
  target_group_arn      = module.alb.target_group_arn
  execution_role_arn    = module.iam.execution_role_arn
  task_role_arn         = module.iam.task_role_arn
  log_group_name        = module.cloudwatch.log_group_name
  backend_image         = var.backend_image != "" ? var.backend_image : module.ecr.backend_repository_url
  cpu                   = var.cpu
  memory                = var.memory

  database_url         = module.rds.database_url
  google_api_key       = var.google_api_key
  openrouter_api_key   = var.openrouter_api_key
  google_client_id     = var.google_client_id
  google_client_secret = var.google_client_secret
  auth_secret          = var.auth_secret
  allowed_origins      = var.allowed_origins
}
