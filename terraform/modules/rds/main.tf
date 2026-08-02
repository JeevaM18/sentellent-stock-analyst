resource "aws_db_subnet_group" "main" {
  name       = "${lower(var.name_prefix)}-db-subnet-group"
  subnet_ids = var.private_subnet_ids

  tags = {
    Name = "${var.name_prefix}-db-subnet-group"
  }
}

resource "aws_db_parameter_group" "pg17" {
  name   = "${lower(var.name_prefix)}-pg17-params"
  family = "postgres17"

  parameter {
    name  = "rds.force_ssl"
    value = "0"
  }

  tags = {
    Name = "${var.name_prefix}-pg17-params"
  }
}

resource "aws_db_instance" "postgres" {
  identifier             = "${lower(var.name_prefix)}-db"
  engine                 = "postgres"
  engine_version         = "17.1"
  instance_class         = "db.t4g.micro"
  allocated_storage      = 20
  max_allocated_storage  = 50
  storage_type           = "gp3"
  publicly_accessible    = false
  multi_az               = false
  skip_final_snapshot    = true
  delete_automated_backups = true

  db_name  = var.db_name
  username = var.db_username
  password = var.db_password

  db_subnet_group_name   = aws_db_subnet_group.main.name
  parameter_group_name   = aws_db_parameter_group.pg17.name
  vpc_security_group_ids = [var.rds_security_group_id]

  backup_retention_period = 7

  tags = {
    Name = "${var.name_prefix}-postgres-db"
  }
}
