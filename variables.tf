variable "ami" {
  description = "The AION AMI.  When not specified latest AMI will be used."
  type        = string
  default     = ""

  validation {
    condition     = var.ami == "" || can(regex("^ami-", var.ami))
    error_message = "Please provide a valid ami id, starting with \"ami-\". or leave blank for latest Spirent AION AMI."
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
  description = "List of management interface ingress IPv4/IPv6 CIDR ranges.  Set to empty list when using security_group_ids."
  type        = list(string)
}

variable "security_group_ids" {
  description = "List of management plane security group IDs.  Leave empty to create a default security group using ingress_cidr_blocks."
  type        = list(string)
  default     = []
}

variable "root_block_device" {
  description = "Customize details about the root block device of the instance. See Block Devices below for details."
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
  description = "Enable provisioning.  When enabled instances will be initialized with the specified variables."
  type        = bool
  default     = true
}

variable "aion_url" {
  description = "AION URL. An example URL would be https://example.spirentaion.com."
  type        = string
}

variable "aion_user" {
  description = "AION user registered on aion_url"
  type        = string
}

variable "aion_password" {
  description = "AION user password for aion_url"
  type        = string
}

variable "cluster_names" {
  description = "Instance cluster names.  List length must equal instance_count."
  type        = list(string)
  default     = []
}

variable "node_names" {
  description = "Instance cluster node names.  List length must equal instance_count."
  type        = list(string)
  default     = []
}

variable "admin_email" {
  description = "Cluster admin user email. Use this to login to instance web page.  Default is obtained from AION user information."
  type        = string
  default     = ""
}

variable "admin_password" {
  description = "Cluster admin user password. Use this to login to to the instance web page."
  type        = string
}

variable "admin_first_name" {
  description = "Cluster admin user first name. Default is obtained from AION user information."
  type        = string
  default     = ""
}

variable "admin_last_name" {
  description = "Cluster admin user last name.  Default is obtained from AION user information."
  type        = string
  default     = ""
}

variable "local_admin_password" {
  description = "Cluster local admin password for instance SSH access.  Will use admin_password if not specified."
  type        = string
  default     = ""
}

variable "node_storage_provider" {
  description = "Cluster node storage provider"
  type        = string
  default     = "local"
}

variable "node_storage_remote_uri" {
  description = "Cluster node storage URI.  Leave blank for default when provider is local"
  type        = string
  default     = ""
}

variable "http_enabled" {
  description = "Allow HTTP access as well as HTTPS.  Normally this is not recommended."
  type        = bool
  default     = false
}

variable "metrics_opt_out" {
  description = "Opt-out of Spirent metrics data collection"
  type        = bool
  default     = false
}

variable "dest_dir" {
  description = "Destination directory on the instance where provisining files will be copied"
  type        = string
  default     = "~"
}
