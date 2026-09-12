# Illustrative GCP deployment, see infra/README.md. Not applied; adapt the
# placeholder values (project id, container image) before use.

terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

variable "project_id" {}

variable "region" {
  default = "us-central1"
}

variable "db_password" {
  sensitive = true
}

variable "dashboard_image" {
  description = "e.g. us-central1-docker.pkg.dev/<project>/ai-data-analyst/dashboard:latest"
}

resource "google_sql_database_instance" "warehouse" {
  name             = "ai-data-analyst-warehouse"
  database_version = "POSTGRES_16"
  region           = var.region

  settings {
    tier = "db-f1-micro"
  }
}

resource "google_sql_database" "analytics" {
  name     = "analytics"
  instance = google_sql_database_instance.warehouse.name
}

resource "google_sql_user" "app" {
  name     = "analyst_app"
  instance = google_sql_database_instance.warehouse.name
  password = var.db_password
}

resource "google_secret_manager_secret" "db_url" {
  secret_id = "ai-data-analyst-database-url"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "db_url" {
  secret      = google_secret_manager_secret.db_url.id
  secret_data = "postgresql+psycopg2://analyst_app:${var.db_password}@/analytics?host=/cloudsql/${google_sql_database_instance.warehouse.connection_name}"
}

resource "google_cloud_run_v2_service" "dashboard" {
  name     = "ai-data-analyst-dashboard"
  location = var.region

  template {
    containers {
      image = var.dashboard_image
      ports {
        container_port = 8501
      }
      env {
        name = "DATABASE_URL"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.db_url.secret_id
            version = "latest"
          }
        }
      }
    }
  }
}

# Scheduled ETL: a Cloud Run Job (not a service) triggered on a cron schedule,
# rather than a long-running process, since the pipeline only needs to run
# periodically.
resource "google_cloud_run_v2_job" "etl" {
  name     = "ai-data-analyst-etl"
  location = var.region

  template {
    template {
      containers {
        image   = var.dashboard_image
        command = ["python", "-m", "pipelines.etl"]
        env {
          name = "DATABASE_URL"
          value_source {
            secret_key_ref {
              secret  = google_secret_manager_secret.db_url.secret_id
              version = "latest"
            }
          }
        }
      }
    }
  }
}

resource "google_cloud_scheduler_job" "nightly_etl" {
  name      = "ai-data-analyst-nightly-etl"
  schedule  = "0 3 * * *" # 03:00 daily
  time_zone = "Etc/UTC"

  http_target {
    http_method = "POST"
    uri         = "https://${var.region}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${var.project_id}/jobs/${google_cloud_run_v2_job.etl.name}:run"
    oauth_token {
      service_account_email = "scheduler-invoker@${var.project_id}.iam.gserviceaccount.com"
    }
  }
}

output "warehouse_connection_name" {
  value = google_sql_database_instance.warehouse.connection_name
}
