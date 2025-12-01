# Muestra el servidor de login del ACR (útil para docker login)
output "acr_login_server" {
  value = module.shared.acr_login_server
}

# Muestra la URL de la API (Arquitectura B)
# Usamos una lógica condicional por si en el futuro despliegas la A
output "app_url_architecture_b" {
  value = var.deploy_arch == "B" || var.deploy_arch == "BOTH" ? module.architecture_b[0].app_url : "No desplegado"
}

output "frontend_deployment_token" {
  value     = module.frontend.deployment_token
  sensitive = true
}

output "frontend_url" {
  value = module.frontend.default_hostname
}