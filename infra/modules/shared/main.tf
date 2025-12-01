# 1. Azure Container Registry (Para guardar la imagen Docker)
resource "azurerm_container_registry" "acr" {
  name                = "acr${var.project_name}"
  resource_group_name = var.resource_group_name
  location            = var.location
  sku                 = "Basic"
  admin_enabled       = true
}

# 2. Red Virtual (VNet) - Necesaria para la VM futura (Arq. A)
resource "azurerm_virtual_network" "vnet" {
  name                = "vnet-${var.project_name}"
  location            = var.location
  resource_group_name = var.resource_group_name
  address_space       = ["10.0.0.0/16"]
}

resource "azurerm_subnet" "subnet" {
  name                 = "subnet-default"
  resource_group_name  = var.resource_group_name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = ["10.0.1.0/24"]
}

# 3. Log Analytics (Para monitorear métricas de Container Apps)
resource "azurerm_log_analytics_workspace" "logs" {
  name                = "logs-${var.project_name}"
  location            = var.location
  resource_group_name = var.resource_group_name
  sku                 = "PerGB2018"
  retention_in_days   = 30
}