# 1. IP Pública para acceder a la VM
resource "azurerm_public_ip" "vm_ip" {
  name                = "pip-yolo-vm"
  location            = var.location
  resource_group_name = var.resource_group_name
  allocation_method   = "Static"   
  sku                 = "Standard" 
}

# 2. Interfaz de Red
resource "azurerm_network_interface" "vm_nic" {
  name                = "nic-yolo-vm"
  location            = var.location
  resource_group_name = var.resource_group_name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = var.subnet_id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.vm_ip.id
  }
}

# 3. Seguridad (Firewall): Abrir puerto 22 (SSH) y 8000 (API)
resource "azurerm_network_security_group" "vm_nsg" {
  name                = "nsg-yolo-vm"
  location            = var.location
  resource_group_name = var.resource_group_name

  security_rule {
    name                       = "AllowSSH"
    priority                   = 1001
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = "*" 
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "AllowAPI"
    priority                   = 1002
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "8000"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
}

resource "azurerm_network_interface_security_group_association" "nsg_assoc" {
  network_interface_id      = azurerm_network_interface.vm_nic.id
  network_security_group_id = azurerm_network_security_group.vm_nsg.id
}

# 4. La Máquina Virtual con GPU (Ahora sí, la real)
resource "azurerm_linux_virtual_machine" "vm" {
  name                = "vm-yolo-gpu"  # Nombre actualizado
  resource_group_name = var.resource_group_name
  location            = var.location
   
  size                = "Standard_NC8as_T4_v3"
  
  admin_username      = "adminuser"
  network_interface_ids = [
    azurerm_network_interface.vm_nic.id,
  ]

  admin_ssh_key {
    username   = "adminuser"
    public_key = file("~/.ssh/id_rsa.pub") 
  }

  # Usamos la imagen "Data Science VM" o "HPC" que ya trae drivers NVIDIA preinstalados
  # Esto nos ahorra horas de instalación manual de drivers.
  source_image_reference {
    publisher = "microsoft-dsvm"
    offer     = "ubuntu-hpc"
    sku       = "2004"
    version   = "latest"
  }

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "StandardSSD_LRS"
  }

  # Script de arranque (User Data)
  # Script de arranque (User Data)
  custom_data = base64encode(<<-EOF
    #!/bin/bash
    # 1. Esperar a que Docker esté listo
    until docker info; do sleep 5; done

    # 2. Login al Registry
    docker login ${var.acr_server} -u ${var.acr_username} -p ${var.acr_admin_password}
    
    # 3. Correr el contenedor
    # Nota: Pasamos la variable WORKERS para que el Dockerfile optimizado lance 8 procesos.
    docker run -d \
      --name yolo_api \
      --restart always \
      --gpus all \
      -p 8000:8000 \
      -e YOLO_MODEL="yolo11n.pt" \
      -e ENABLE_BATCHING="${var.enable_batching}" \
      -e BATCH_SIZE="${var.enable_batching == "true" ? "32" : "8"}" \
      -e WORKERS="8" \
      ${var.acr_server}/yolo-api:latest
  EOF
  )
}