


# find latest Spirent AION AMI
data "aws_ami" "aion" {
  owners           = ["679593333241"]
  most_recent      = true
  executable_users = ["all"]

  filter {
    name   = "name"
    values = ["*aion-platform-image-*"]
  }
}

resource "aws_security_group" "aion" {
  count       = length(var.security_group_ids) > 0 ? 0 : 1
  name        = "aion-${random_id.uid.id}"
  description = "AION Security Group"

  vpc_id = var.vpc_id

  # HTTP
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = var.ingress_cidr_blocks
  }

  # HTTPS
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = var.ingress_cidr_blocks
  }

  # SSH
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.ingress_cidr_blocks
  }

  # Application usage
  ingress {
    from_port   = 64000
    to_port     = 64999
    protocol    = "tcp"
    cidr_blocks = var.ingress_cidr_blocks
  }

  # LabServer Session Manager
  ingress {
    from_port   = 49000
    to_port     = 50000
    protocol    = "tcp"
    cidr_blocks = var.ingress_cidr_blocks
  }

  # ICMP
  ingress {
    from_port   = -1
    to_port     = -1
    protocol    = "icmp"
    cidr_blocks = var.ingress_cidr_blocks
  }

  # ICMPv6
  ingress {
    from_port   = -1
    to_port     = -1
    protocol    = "icmpv6"
    cidr_blocks = var.ingress_cidr_blocks
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "random_id" "uid" {
  byte_length = 8
}

data "tls_public_key" "user" {
  private_key_pem = file(var.private_key_file)
}

data "template_file" "user_data" {
  template = file("${path.module}/user_data.tpl")
  vars = {
    ssh_auth_key = data.tls_public_key.user.public_key_openssh
  }
}

# create AION
resource "aws_instance" "aion" {
  count         = var.instance_count
  ami           = var.ami != "" ? var.ami : data.aws_ami.aion.id
  instance_type = var.instance_type
  key_name      = var.key_name

  user_data = data.template_file.user_data.rendered

  dynamic "root_block_device" {
    for_each = length(var.root_block_device) > 0 ? var.root_block_device : [{}]
    content {
      delete_on_termination = lookup(root_block_device.value, "delete_on_termination", true)
      encrypted             = lookup(root_block_device.value, "encrypted", null)
      iops                  = lookup(root_block_device.value, "iops", null)
      kms_key_id            = lookup(root_block_device.value, "kms_key_id", null)
      volume_size           = lookup(root_block_device.value, "volume_size", null)
      volume_type           = lookup(root_block_device.value, "volume_type", null)
    }
  }

  network_interface {
    network_interface_id = aws_network_interface.mgmt_plane[count.index].id
    device_index         = 0
  }

  tags = {
    Name = format("%s%d", var.instance_name_prefix, 1 + count.index)
  }
}

resource "aws_network_interface" "mgmt_plane" {
  count           = var.instance_count
  subnet_id       = var.subnet_id
  security_groups = length(var.security_group_ids) > 0 ? var.security_group_ids : [aws_security_group.aion[0].id]
}

resource "aws_eip_association" "public_ip" {
  count                = length(var.eips)
  network_interface_id = aws_network_interface.mgmt_plane[count.index].id
  allocation_id        = var.eips[count.index]
}

data "template_file" "setup_aion" {
  count    = var.enable_provisioner ? var.instance_count : 0
  template = file("${path.module}/setup-aion.tpl")
  vars = {
    script_file             = "${var.dest_dir}/setup-aion.py"
    platform_addr           = aws_instance.aion[count.index].public_ip
    aion_url                = var.aion_url
    aion_user               = var.aion_user
    aion_password           = var.aion_password
    cluster_name            = length(var.cluster_names) < 1 ? "" : var.cluster_names[count.index]
    node_name               = length(var.node_names) < 1 ? "" : var.node_names[count.index]
    admin_email             = var.admin_email
    admin_first_name        = var.admin_first_name
    admin_last_name         = var.admin_last_name
    admin_password          = var.admin_password
    local_admin_password    = var.local_admin_password
    node_storage_provider   = var.node_storage_provider
    node_storage_remote_uri = var.node_storage_remote_uri
    metrics_opt_out         = var.metrics_opt_out
    http_enabled            = var.http_enabled
    deploy_location         = var.deploy_location
    deploy_products         = jsonencode(var.deploy_products)
    entitlements            = jsonencode(var.entitlements)
  }
}

data "template_file" "release_aion" {
  count    = var.enable_provisioner ? var.instance_count : 0
  template = file("${path.module}/release-aion.tpl")
  vars = {
    script_file          = "${var.dest_dir}/release-aion.py"
    platform_addr        = aws_instance.aion[count.index].public_ip
    aion_url             = var.aion_url
    aion_user            = var.aion_user
    aion_password        = var.aion_password
    admin_email          = var.admin_email
    admin_password       = var.admin_password
    local_admin_password = var.local_admin_password
  }
}

# provison the AION VM
resource "null_resource" "provisioner" {
  count = var.enable_provisioner ? var.instance_count : 0
  triggers = {
    dest_dir    = var.dest_dir
    host        = aws_instance.aion[count.index].public_ip
    private_key = file(var.private_key_file)
  }
  connection {
    host        = self.triggers.host
    type        = "ssh"
    user        = "debian"
    private_key = self.triggers.private_key
    agent       = false
  }

  # force provisioners to rerun
  # triggers = {
  #   always_run = "${timestamp()}"
  # }

  # copy install script
  provisioner "file" {
    source      = "${path.module}/setup-aion.py"
    destination = "${var.dest_dir}/setup-aion.py"
  }

  provisioner "file" {
    content     = data.template_file.setup_aion[count.index].rendered
    destination = "${var.dest_dir}/setup-aion.sh"
  }

  provisioner "file" {
    source      = "${path.module}/release-aion.py"
    destination = "${var.dest_dir}/release-aion.py"
  }

  provisioner "file" {
    content     = data.template_file.release_aion[count.index].rendered
    destination = "${var.dest_dir}/release-aion.sh"
  }

  # run setup AION
  provisioner "remote-exec" {
    inline = [
      "bash ${var.dest_dir}/setup-aion.sh"
    ]
  }

  # destroy provisioner
  provisioner "remote-exec" {
    when = destroy
    inline = [
      "bash ${self.triggers.dest_dir}/release-aion.sh"
    ]
  }
}
