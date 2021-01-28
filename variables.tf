variable "ami" {
  description = "The AION AMI.  When not specified latests AMI will be used."
  type        = string
  default     = ""

  validation {
    condition     = var.ami == "" || can(regex("^ami-", var.ami))
    error_message = "Please provide a valid ami id, starting with \"ami-\". or leave blank for latest Windows Server 2019 AMI."
  }
}

variable "vpc_id" {
  description = "AWS VPC ID"
  type        = string

  validation {
    condition     = can(regex("^vpc-", var.vpc_id))
    error_message = "Please provide a valid vpc id, starting with \"vpc-\"."
  }
}

variable "instance_name_prefix" {
  description = "Name assigned to the AION platform instance.  An instance number will be appended to the name."
  type        = string
  default     = "aion-"
}

variable "instance_count" {
  description = "Number of instances to create"
  type        = number
  default     = 1
}

variable "instance_type" {
  description = "AWS instance type"
  type        = string
  default     = "m5.large"
}

variable "subnet_id" {
  description = "Management public AWS subnet ID"
  type        = string

  validation {
    condition     = can(regex("^subnet-", var.subnet_id))
    error_message = "Please provide a valid subnet id, starting with \"subnet-\"."
  }
}

variable "eips" {
  description = "List of management plane elastic IP IDs.  Leave empty if subnet auto assigns IPs."
  type        = list(string)
  default     = []
}

variable "ingress_cidr_blocks" {
  description = "List of management interface ingress IPv4/IPv6 CIDR ranges"
  type        = list(string)
}

variable "root_block_device" {
  description = " Customize details about the root block device of the instance. See Block Devices below for details."
  type        = list(map(string))
  default     = []
}

variable "key_name" {
  description = "AWS SSH key name to assign to each instance"
  type        = string
}

variable "private_key_file" {
  description = "AWS key private file"
  type        = string
}

variable "enable_provisioner" {
  description = "Enable provisioning"
  type        = bool
  default     = true
}

variable "aion_url" {
  description = "AION URL"
  type        = string
  default     = "https://spirentaion.com"
}

variable "aion_user" {
  description = "AION user"
  type        = string
}

variable "aion_password" {
  description = "AION password"
  type        = string
}

variable "cluster_names" {
  description = "Instance cluster names.  List length must equal instance_count."
  type        = list(string)
  default     = []
}

variable "node_names" {
  description = "Instance node names.  List length must equal instance_count."
  type        = list(string)
  default     = []
}

variable "admin_first_name" {
  description = "Admin first name"
  type        = string
  default     = ""
}

variable "admin_last_name" {
  description = "Admin last name"
  type        = string
  default     = ""
}

variable "admin_password" {
  description = "Admin password"
  type        = string
}

variable "local_admin_password" {
  description = "Local admin password.  Will use admin_password if not specified."
  type        = string
  default     = ""
}

variable "node_storage_provider" {
  description = "Node storage provider"
  type        = string
  default     = "local"
}

variable "node_storage_remote_uri" {
  description = "Node storage URI"
  type        = string
  default     = ""
}

variable "dest_dir" {
  description = "Destination directory on the instance where files will be copied"
  type        = string
  default     = "~"
}
