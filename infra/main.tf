# --- RECURSOS COMPARTIDOS ---
resource "azurerm_resource_group" "rg" {
  name     = "rg-tesis-yolo-${var.project_name}"
  location = var.location
}

module "shared" {
  source              = "./modules/shared"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  project_name        = var.project_name
}

# --- ARQUITECTURA A (IaaS - VM) ---
module "architecture_a" {
  count  = var.deploy_arch == "A" || var.deploy_arch == "BOTH" ? 1 : 0
  source = "./modules/architecture_a"

  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  subnet_id           = module.shared.subnet_id
  acr_server          = module.shared.acr_login_server
  acr_username        = module.shared.acr_admin_username
  acr_admin_password  = module.shared.acr_admin_password
  enable_batching = var.enable_batching
}

# --- ARQUITECTURA B (CaaS - Serverless) ---
module "architecture_b" {
  count  = var.deploy_arch == "B" || var.deploy_arch == "BOTH" ? 1 : 0
  source = "./modules/architecture_b"

  project_name          = var.project_name
  resource_group_name   = azurerm_resource_group.rg.name
  location              = azurerm_resource_group.rg.location
  acr_login_server      = module.shared.acr_login_server
  acr_admin_username    = module.shared.acr_admin_username
  acr_admin_password    = module.shared.acr_admin_password
  log_analytics_workspace_id = module.shared.log_analytics_workspace_id
  enable_batching = var.enable_batching
}

# --- FRONTEND (React Static Web App) ---
module "frontend" {
  source              = "./modules/frontend"
  project_name        = var.project_name
  resource_group_name = azurerm_resource_group.rg.name
  # Static Web Apps es un servicio global, pero los metadatos se guardan en una región.
  # "eastus2" suele ser la recomendada para esto.
  location            = "eastus2" 
}