provider "aws" {
  region = "us-east-1"
}


data "aws_vpc" "default" {
  default = true
}

module "aion" {
  source = "../.."
  ami =  "ami-03a87b10a193257d1"
  vpc_id         = data.aws_vpc.default.id

  subnet_id           = "subnet-ffe75cb2"
  ingress_cidr_blocks = ["0.0.0.0/0"]

  key_name         = "stcv_dev_key"
  private_key_file = "~/.ssh/stcv_dev_key.pem"

  aion_user = "Richard.Myers@spirent.com"
  aion_password = "smtm5536"
  admin_password = "spirent123!"

  root_block_device = [
    {
      volume_type = "gp2"
      volume_size = 60
    }
  ]
}

output setup_aion_sh {
  description = "Setup AION SH"
  value       = module.aion.setup_aion_sh

}

output "instance_public_ips" {
  value = module.aion.instance_public_ips
}
