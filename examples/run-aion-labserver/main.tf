provider "aws" {
  region = var.region
}

variable "region" {
  description = "AWS region"
  default     = "us-west-2"
}

variable "vpc_id" {
  description = "VPC ID"
  default     = "vpc-123456789"
}

variable "subnet_id" {
  description = "Management plane subnet ID"
  default     = "subnet-123456789"
}

variable "key_name" {
  description = "AWS SSH key name to assign to each instance"
  default     = "bootstrap_key"
}

variable "private_key_file" {
  description = "AWS key private file"
  default     = "bootstrap_private_key_file"
}

variable "aion_url" {
  description = "AION URL."
  default     = "https://spirent.spirentaion.com"
}

variable "aion_user" {
  description = "AION user. Specify using command line or env variables."
}

variable "aion_password" {
  description = "AION password. Specify using command line or env variables."
}

variable "admin_password" {
  description = "New cluster admin password. Specify using command line or env variables."
}


module "aion" {
  source = "../.."
  vpc_id = var.vpc_id

  subnet_id = var.subnet_id
  # Warning: Using all address cidr block to simplify the example. You should limit instance access.
  ingress_cidr_blocks = ["0.0.0.0/0"]

  key_name         = var.key_name
  private_key_file = var.private_key_file

  aion_url       = var.aion_url
  aion_user      = var.aion_user
  aion_password  = var.aion_password
  admin_password = var.admin_password
  http_enabled   = true

  instance_type = "m5.2xlarge"
  root_block_device = [
    {
      volume_type = "gp2"
      volume_size = 100
    }
  ]

  deploy_location = "labserver"
  deploy_products = [
    {
      name    = "STC LabServer"
      version = "5.30.0136"
    }
  ]

  entitlements = [
    {
      product = "Spirent TestCenter"
      license = "Virtual High Scale Bandwidth"
      number  = 1000
    },
    {
      product = "Spirent TestCenter"
      license = "Access"
      number  = 100
    }
  ]
}

output "instance_public_ips" {
  description = "List of public IP addresses assigned to the instances, if applicable"
  value       = module.aion.instance_public_ips
}
