variable "resource_group_name" { type = string }
variable "location" { type = string }
variable "subnet_id" { type = string }
variable "acr_server" { type = string }
variable "acr_username" { type = string }

variable "acr_admin_password" { 
  type = string 
  sensitive = true 
}

variable "enable_batching" {
  description = "Habilitar Adaptive Batching (true/false)"
  type        = string
}