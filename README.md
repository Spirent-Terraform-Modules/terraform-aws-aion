
# Spirent AION Platform Terraform

## Description

Run Spirent AION platform instances.  After Terraform apply finishes you will be able to point your browser at the instance_public_ips addresses.

If you would like to configure the Spirent AION platform in a web browser set the variable enable_provisioner=false.  Otherwise when enable_provisioner=true the instance will be configured however license entitlement & product installation should be completed in your web browser (see below).

### Add License Entitlements
1. Navigate to "License Manager" "Entitlements"
2. Click on "Install Entitlements"
3. Use one of the following methods to add entitlements (#1 is prefered)
   1. Login to <your_org>.spirentaion.com and select entitlements to host in the new instance
      Note: Hosted entitlements should be released before destroying the instance.  When entitlements are not released you will need to contact Spirent support to release them for you.
   2. Install a license entitlement file obtained from Spirent support

### Add Products
1. Navigate to "Settings" "Add New Products"
2. Click "Install New Products"
3. Select products and versions and click "Install"


<!-- BEGINNING OF PRE-COMMIT-TERRAFORM DOCS HOOK -->
## Requirements

| Name | Version |
|------|---------|
| terraform | >= 0.13.0 |
| aws | >= 2.65 |

## Providers

| Name | Version |
|------|---------|
| aws | >= 2.65 |
| null | n/a |
| template | n/a |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| admin\_email | Cluster admin user email. Use this to login to instance web page.  Default is obtained from AION user information. | `string` | `""` | no |
| admin\_first\_name | Cluster admin user first name. Default is obtained from AION user information. | `string` | `""` | no |
| admin\_last\_name | Cluster admin user last name.  Default is obtained from AION user information. | `string` | `""` | no |
| admin\_password | Cluster admin user password. Use this to login to to the instance web page. | `string` | n/a | yes |
| aion\_password | AION user password for aion\_url | `string` | n/a | yes |
| aion\_url | AION URL. An example URL would be https://example.spirentaion.com. | `string` | n/a | yes |
| aion\_user | AION user registered on aion\_url | `string` | n/a | yes |
| ami | The AION AMI.  When not specified latest AMI will be used. | `string` | `""` | no |
| cluster\_names | Instance cluster names.  List length must equal instance\_count. | `list(string)` | `[]` | no |
| dest\_dir | Destination directory on the instance where provisining files will be copied | `string` | `"~"` | no |
| eips | List of management plane elastic IP IDs.  Leave empty if subnet auto assigns IPs. | `list(string)` | `[]` | no |
| enable\_provisioner | Enable provisioning.  When enabled instances will be initialized with the specified variables. | `bool` | `true` | no |
| http\_enabled | Allow HTTP access as well as HTTPS.  Normally this is not recommended. | `bool` | `false` | no |
| ingress\_cidr\_blocks | List of management interface ingress IPv4/IPv6 CIDR ranges | `list(string)` | n/a | yes |
| instance\_count | Number of instances to create | `number` | `1` | no |
| instance\_name\_prefix | Name assigned to the AION platform instance.  An instance number will be appended to the name. | `string` | `"aion-"` | no |
| instance\_type | AWS instance type | `string` | `"m5.large"` | no |
| key\_name | AWS SSH key name to assign to each instance | `string` | n/a | yes |
| local\_admin\_password | Cluster local admin password for instance SSH access.  Will use admin\_password if not specified. | `string` | `""` | no |
| metrics\_opt\_out | Opt-out of Spirent metrics data collection | `bool` | `false` | no |
| node\_names | Instance cluster node names.  List length must equal instance\_count. | `list(string)` | `[]` | no |
| node\_storage\_provider | Cluster node storage provider | `string` | `"local"` | no |
| node\_storage\_remote\_uri | Cluster node storage URI.  Leave blank for default when provider is local | `string` | `""` | no |
| private\_key\_file | AWS key private file | `string` | n/a | yes |
| root\_block\_device | Customize details about the root block device of the instance. See Block Devices below for details. | `list(map(string))` | `[]` | no |
| subnet\_id | Management public AWS subnet ID | `string` | n/a | yes |
| vpc\_id | AWS VPC ID | `string` | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| instance\_ids | List of instance IDs |
| instance\_private\_ips | List of private IP addresses assigned to the instances, if applicable |
| instance\_public\_ips | List of public IP addresses assigned to the instances, if applicable |

<!-- END OF PRE-COMMIT-TERRAFORM DOCS HOOK -->

## Block Devices

### Root Block Device
The root_block_device mapping supports the following:

* delete_on_termination - (Optional) Whether the volume should be destroyed on instance termination. Defaults to true.
* encrypted - (Optional) Whether to enable volume encryption. Defaults to false. Must be configured to perform drift detection.
* iops - (Optional) Amount of provisioned IOPS. Only valid for volume_type of io1, io2 or gp3.
* kms_key_id - (Optional) Amazon Resource Name (ARN) of the KMS Key to use when encrypting the volume. Must be configured to perform drift detection.
* tags - (Optional) A map of tags to assign to the device.
* throughput - (Optional) Throughput to provision for a volume in mebibytes per second (MiB/s). This is only valid for volume_type of gp3.
* volume_size - (Optional) Size of the volume in gibibytes (GiB).
* volume_type - (Optional) Type of volume. Valid values include standard, gp2, gp3, io1, io2, sc1, or st1. Defaults to gp2.
