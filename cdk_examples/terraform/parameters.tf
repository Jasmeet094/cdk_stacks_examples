terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }

  required_version = ">= 1.2.0"
}

provider "aws" {
  region = "us-east-1"
  profile = var.aws_profile
}

variable "aws_profile" {
  description = "AWS profile to use"
  type        = string
  default     = "test-demo"
}

variable "parameters" {
  description = "List of parameter names"
  type        = list(string)
  default     = ["test-current-environment", 
                 "test-ng-admin-api-commit-id",
                 "test-ng-admin-commit-id",
                 "test-ng-api-commit-id",
                 "test-ng-app-commit-id",
                 "test-ng-notifications-commit-id",
                 "test-ng-portal-api-commit-id",
                 "test-ng-services-api-commit-id"]
}

resource "aws_ssm_parameter" "example" {
  count       = length(var.parameters)
  name        = var.parameters[count.index]
  type        = "String"
  value       = "latest"
  overwrite   = true
}