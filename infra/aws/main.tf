# Illustrative AWS deployment — see infra/README.md. Not applied; adapt the
# placeholder values (container image, VPC/subnet ids, secrets) before use.

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

variable "aws_region" {
  default = "us-east-1"
}

variable "db_username" {
  default = "analyst_app"
}

variable "db_password" {
  sensitive = true
  # Set via TF_VAR_db_password or a secrets backend — never commit a real value.
}

variable "vpc_subnet_ids" {
  type        = list(string)
  description = "Subnet ids for RDS + ECS networking"
}

variable "dashboard_image" {
  description = "Container image for dashboard/app.py, e.g. <account>.dkr.ecr.<region>.amazonaws.com/ai-data-analyst-dashboard:latest"
}

resource "aws_db_instance" "warehouse" {
  identifier             = "ai-data-analyst-warehouse"
  engine                 = "postgres"
  engine_version         = "16"
  instance_class         = "db.t4g.micro"
  allocated_storage      = 20
  db_name                = "analytics"
  username               = var.db_username
  password               = var.db_password
  skip_final_snapshot    = true
  publicly_accessible    = false
  backup_retention_period = 7
}

resource "aws_secretsmanager_secret" "db_url" {
  name = "ai-data-analyst/database-url"
}

resource "aws_secretsmanager_secret_version" "db_url" {
  secret_id = aws_secretsmanager_secret.db_url.id
  secret_string = "postgresql+psycopg2://${var.db_username}:${var.db_password}@${aws_db_instance.warehouse.address}:5432/analytics"
}

resource "aws_ecs_cluster" "this" {
  name = "ai-data-analyst"
}

resource "aws_ecs_task_definition" "dashboard" {
  family                   = "ai-data-analyst-dashboard"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "512"

  container_definitions = jsonencode([
    {
      name      = "dashboard"
      image     = var.dashboard_image
      essential = true
      portMappings = [{ containerPort = 8501, protocol = "tcp" }]
      secrets = [
        { name = "DATABASE_URL", valueFrom = aws_secretsmanager_secret.db_url.arn }
      ]
    }
  ])
}

resource "aws_ecs_service" "dashboard" {
  name            = "ai-data-analyst-dashboard"
  cluster         = aws_ecs_cluster.this.id
  task_definition = aws_ecs_task_definition.dashboard.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.vpc_subnet_ids
    assign_public_ip = true
  }
}

# Scheduled ETL: runs pipelines/etl.py as a one-off Fargate task on a schedule
# instead of a long-running service, since it only needs to run periodically.
resource "aws_ecs_task_definition" "etl" {
  family                   = "ai-data-analyst-etl"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "512"

  container_definitions = jsonencode([
    {
      name      = "etl"
      image     = var.dashboard_image # same image, different entrypoint/command
      essential = true
      command   = ["python", "-m", "pipelines.etl"]
      secrets = [
        { name = "DATABASE_URL", valueFrom = aws_secretsmanager_secret.db_url.arn }
      ]
    }
  ])
}

resource "aws_scheduler_schedule" "nightly_etl" {
  name                = "ai-data-analyst-nightly-etl"
  schedule_expression = "cron(0 3 * * ? *)" # 03:00 UTC daily

  flexible_time_window {
    mode = "OFF"
  }

  target {
    arn      = aws_ecs_cluster.this.arn
    role_arn = aws_iam_role.scheduler.arn

    ecs_parameters {
      task_definition_arn = aws_ecs_task_definition.etl.arn
      launch_type          = "FARGATE"

      network_configuration {
        subnets          = var.vpc_subnet_ids
        assign_public_ip = true
      }
    }
  }
}

resource "aws_iam_role" "scheduler" {
  name = "ai-data-analyst-scheduler-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "scheduler.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

output "warehouse_endpoint" {
  value = aws_db_instance.warehouse.address
}
