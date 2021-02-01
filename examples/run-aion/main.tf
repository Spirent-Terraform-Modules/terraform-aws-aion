provider "aws" {
  region = "us-east-1"
}


data "aws_vpc" "default" {
  default = true
}

module "aion" {
  source = "../.."
  vpc_id = data.aws_vpc.default.id

  subnet_id = "subnet-ffe75cb2"
  # Warning: Using all adddress cidr block to simplify the example. You should limit instance access.
  ingress_cidr_blocks = ["0.0.0.0/0"]

  key_name         = "stcv_dev_key"
  private_key_file = "~/.ssh/stcv_dev_key.pem"

  aion_url       = "https://spirent.spirentaion.com"
  aion_user      = var.aion_user
  aion_password  = var.aion_password
  admin_password = var.admin_password

  root_block_device = [
    {
      volume_type = "gp2"
      volume_size = 60
    }
  ]
}

# output "setup_aion_sh" {
#   description = "Setup AION SH"
#   value       = module.aion.setup_aion_sh
# }

output "instance_public_ips" {
  value = module.aion.instance_public_ips
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
