# Illustrative Azure deployment, see infra/README.md. Not applied; adapt the
# placeholder values (resource group, container image) before use.

terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
}

variable "resource_group_name" {
  default = "ai-data-analyst-rg"
}

variable "location" {
  default = "eastus"
}

variable "db_password" {
  sensitive = true
}

variable "dashboard_image" {
  description = "e.g. aidataanalyst.azurecr.io/dashboard:latest"
}

resource "azurerm_resource_group" "this" {
  name     = var.resource_group_name
  location = var.location
}

resource "azurerm_postgresql_flexible_server" "warehouse" {
  name                   = "ai-data-analyst-warehouse"
  resource_group_name    = azurerm_resource_group.this.name
  location               = azurerm_resource_group.this.location
  version                = "16"
  administrator_login    = "analyst_app"
  administrator_password = var.db_password
  storage_mb             = 32768
  sku_name               = "B_Standard_B1ms"
}

resource "azurerm_key_vault" "this" {
  name                = "ai-data-analyst-kv"
  resource_group_name = azurerm_resource_group.this.name
  location            = azurerm_resource_group.this.location
  tenant_id           = data.azurerm_client_config.current.tenant_id
  sku_name            = "standard"
}

data "azurerm_client_config" "current" {}

resource "azurerm_key_vault_secret" "db_url" {
  name         = "database-url"
  value        = "postgresql+psycopg2://analyst_app:${var.db_password}@${azurerm_postgresql_flexible_server.warehouse.fqdn}:5432/analytics"
  key_vault_id = azurerm_key_vault.this.id
}

resource "azurerm_container_app_environment" "this" {
  name                = "ai-data-analyst-env"
  resource_group_name = azurerm_resource_group.this.name
  location            = azurerm_resource_group.this.location
}

resource "azurerm_container_app" "dashboard" {
  name                         = "ai-data-analyst-dashboard"
  resource_group_name         = azurerm_resource_group.this.name
  container_app_environment_id = azurerm_container_app_environment.this.id
  revision_mode                = "Single"

  template {
    container {
      name   = "dashboard"
      image  = var.dashboard_image
      cpu    = 0.5
      memory = "1Gi"
      env {
        name        = "DATABASE_URL"
        secret_name = "database-url"
      }
    }
  }

  secret {
    name  = "database-url"
    value = azurerm_key_vault_secret.db_url.value
  }

  ingress {
    external_enabled = true
    target_port      = 8501
    traffic_weight {
      percentage = 100
    }
  }
}

# Scheduled ETL: a Container Apps Job with a cron trigger, rather than a
# long-running app, since the pipeline only needs to run periodically.
resource "azurerm_container_app_job" "etl" {
  name                         = "ai-data-analyst-etl"
  resource_group_name         = azurerm_resource_group.this.name
  location                     = azurerm_resource_group.this.location
  container_app_environment_id = azurerm_container_app_environment.this.id

  replica_timeout_in_seconds = 1800
  replica_retry_limit        = 1

  schedule_trigger_config {
    cron_expression = "0 3 * * *" # 03:00 daily
  }

  template {
    container {
      name    = "etl"
      image   = var.dashboard_image
      cpu     = 0.5
      memory  = "1Gi"
      command = ["python", "-m", "pipelines.etl"]
      env {
        name        = "DATABASE_URL"
        secret_name = "database-url"
      }
    }
  }

  secret {
    name  = "database-url"
    value = azurerm_key_vault_secret.db_url.value
  }
}

output "warehouse_fqdn" {
  value = azurerm_postgresql_flexible_server.warehouse.fqdn
}
