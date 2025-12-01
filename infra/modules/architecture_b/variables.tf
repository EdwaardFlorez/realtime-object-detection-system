variable "project_name" { type = string }
variable "location" { type = string }
variable "resource_group_name" { type = string }
variable "acr_login_server" { type = string }
variable "acr_admin_username" { type = string }
variable "acr_admin_password" { type = string }
variable "log_analytics_workspace_id" { type = string }

variable "enable_batching" {
  description = "Habilitar Adaptive Batching (true/false)"
  type        = string
}