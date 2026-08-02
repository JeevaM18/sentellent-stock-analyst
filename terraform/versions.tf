terraform {
  required_version = ">= 1.8.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.50"
    }
  }

  # Optional Remote S3 Backend Configuration (Uncomment for Team/Production CI/CD State Locking)
  # backend "s3" {
  #   bucket         = "sentellent-terraform-state-bucket"
  #   key            = "production/terraform.tfstate"
  #   region         = "ap-south-1"
  #   dynamodb_table = "sentellent-terraform-locks"
  #   encrypt        = true
  # }
}
