resource "azurerm_static_site" "web" {
  name                = "stapp-${var.project_name}"
  resource_group_name = var.resource_group_name
  location            = var.location
  sku_tier            = "Standard" # Standard es necesario para dominios personalizados
  sku_size            = "Standard"
}