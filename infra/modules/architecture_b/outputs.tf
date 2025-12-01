output "app_url" {
  value = "https://${azurerm_container_app.yolo_app.ingress[0].fqdn}"
}