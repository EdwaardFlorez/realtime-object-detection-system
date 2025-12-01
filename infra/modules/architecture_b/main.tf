resource "azurerm_container_app_environment" "env" {
  name                       = "cae-${var.project_name}"
  location                   = var.location
  resource_group_name        = var.resource_group_name
  log_analytics_workspace_id = var.log_analytics_workspace_id
}

resource "azurerm_container_app" "yolo_app" {
  name                         = "ca-yolo-api"
  container_app_environment_id = azurerm_container_app_environment.env.id
  resource_group_name          = var.resource_group_name
  revision_mode                = "Single"

  template {
    container {
      name   = "yolo-container"
      image  = "${var.acr_login_server}/yolo-api:latest"
      
      # Recursos para inferencia
      cpu    = 2.0
      memory = "4.0Gi"

      # Variables de Entorno (SOLO EL MODELO, SIN STORAGE)
      env {
        name  = "YOLO_MODEL"
        value = "yolo11n.pt"
      }

      env {
        name  = "ENABLE_BATCHING"
        value = var.enable_batching # "true" o "false"
      }
      env {
        name  = "BATCH_SIZE"
        value = "8" # O lo que quieras probar
      }
    }

    # Políticas de Escalado
    min_replicas = 1
    max_replicas = 10
    
    custom_scale_rule {
      name      = "http-scale-rule"
      custom_rule_type = "http"
      metadata = {
        concurrentRequests = "10"
      }
    }
  }

  ingress {
    external_enabled = true
    target_port      = 8000
    traffic_weight {
      percentage = 100
      latest_revision = true
    }
  }

  registry {
    server               = var.acr_login_server
    username             = var.acr_admin_username
    password_secret_name = "acr-password"
  }

  secret {
    name  = "acr-password"
    value = var.acr_admin_password
  }
}