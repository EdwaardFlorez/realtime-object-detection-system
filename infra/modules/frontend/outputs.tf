output "deployment_token" {
  value     = azurerm_static_site.web.api_key
  sensitive = true
}

output "default_hostname" {
  value = azurerm_static_site.web.default_host_name
}