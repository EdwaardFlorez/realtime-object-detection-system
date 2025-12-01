variable "subscription_id" {
  description = "ID de la suscripción de Azure"
  type        = string
}

variable "project_name" {
  description = "Nombre del proyecto"
  type        = string
}

variable "location" {
  description = "Región de Azure"
  type        = string
  default     = "eastus"
}

variable "deploy_arch" {
  description = "Arquitectura a desplegar: 'A', 'B' o 'BOTH'"
  type        = string
  default     = "B"
}

variable "enable_batching" {
  description = "Activar patrón de Adaptive Batching"
  type        = string
  default     = "false"
}