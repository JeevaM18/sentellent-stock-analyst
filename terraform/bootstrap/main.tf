terraform {
  required_version = ">= 1.8.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.50"
    }
  }
}

provider "aws" {
  region = "ap-south-1"
}

# 1. S3 Bucket for Terraform Remote State
resource "aws_s3_bucket" "terraform_state" {
  bucket        = "sentellent-terraform-state-ap-south-1"
  force_destroy = false

  tags = {
    Name        = "sentellent-terraform-state"
    Project     = "Sentellent"
    Environment = "Production"
    ManagedBy   = "Terraform"
  }
}

resource "aws_s3_bucket_versioning" "state_versioning" {
  bucket = aws_s3_bucket.terraform_state.id
  versioning_configuration {
    status = "ENABLED"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "state_encryption" {
  bucket = aws_s3_bucket.terraform_state.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "state_public_block" {
  bucket = aws_s3_bucket.terraform_state.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# 2. DynamoDB Table for Terraform State Locking
resource "aws_dynamodb_table" "terraform_locks" {
  name         = "sentellent-terraform-locks"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  tags = {
    Name        = "sentellent-terraform-locks"
    Project     = "Sentellent"
    Environment = "Production"
    ManagedBy   = "Terraform"
  }
}
