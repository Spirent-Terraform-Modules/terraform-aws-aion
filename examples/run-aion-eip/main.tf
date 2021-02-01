provider "aws" {
  region = "us-west-2"
}

data "aws_vpc" "default" {
  tags = {
    ExampleName = "vpc1"
  }
}

data "aws_subnet" "mgmt_plane" {
  vpc_id = data.aws_vpc.default.id
  tags = {
    ExampleName = "mgmt_plane"
  }
}

data "aws_eip" "eip1" {
  tags = {
    ExampleName = "eip2"
  }
}

module "aion" {
  source = "../.."

  vpc_id         = data.aws_vpc.default.id
  instance_count = 1

  subnet_id = data.aws_subnet.mgmt_plane.id
  eips      = [data.aws_eip.eip1.id]

  ingress_cidr_blocks = ["0.0.0.0/0"]
  key_name            = "spirent_ec2"
  private_key_file    = "~/.ssh/spirent_ec2"

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
