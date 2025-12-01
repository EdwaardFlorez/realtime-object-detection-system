output "acr_login_server" { value = azurerm_container_registry.acr.login_server }
output "acr_admin_username" { value = azurerm_container_registry.acr.admin_username }
output "acr_admin_password" { value = azurerm_container_registry.acr.admin_password }
output "subnet_id" { value = azurerm_subnet.subnet.id }
output "log_analytics_workspace_id" { value = azurerm_log_analytics_workspace.logs.id }
output "acr_id" { value = azurerm_container_registry.acr.id }