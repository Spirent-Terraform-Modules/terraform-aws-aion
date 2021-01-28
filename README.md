
# Spirent AION 

Spirent AION platform 


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
| admin\_first\_name | Admin first name | `string` | `""` | no |
| admin\_last\_name | Admin last name | `string` | `""` | no |
| admin\_password | Admin password | `string` | n/a | yes |
| aion\_password | AION password | `string` | n/a | yes |
| aion\_url | AION URL | `string` | `"https://spirentaion.com"` | no |
| aion\_user | AION user | `string` | n/a | yes |
| ami | The AION AMI.  When not specified latests AMI will be used. | `string` | `""` | no |
| cluster\_names | Instance cluster names.  List length must equal instance\_count. | `list(string)` | `[]` | no |
| dest\_dir | Destination directory on the instance where files will be copied | `string` | `"~"` | no |
| eips | List of management plane elastic IP IDs.  Leave empty if subnet auto assigns IPs. | `list(string)` | `[]` | no |
| enable\_provisioner | Enable provisioning | `bool` | `true` | no |
| ingress\_cidr\_blocks | List of management interface ingress IPv4/IPv6 CIDR ranges | `list(string)` | n/a | yes |
| instance\_count | Number of instances to create | `number` | `1` | no |
| instance\_name\_prefix | Name assigned to the AION platform instance.  An instance number will be appended to the name. | `string` | `"aion-"` | no |
| instance\_type | AWS instance type | `string` | `"m5.large"` | no |
| key\_name | AWS SSH key name to assign to each instance | `string` | n/a | yes |
| local\_admin\_password | Local admin password.  Will use admin\_password if not specified. | `string` | `""` | no |
| node\_names | Instance node names.  List length must equal instance\_count. | `list(string)` | `[]` | no |
| node\_storage\_provider | Node storage provider | `string` | `"local"` | no |
| node\_storage\_remote\_uri | Node storage URI | `string` | `""` | no |
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
| setup\_aion\_sh | Setup AION script |

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
*volume_type - (Optional) Type of volume. Valid values include standard, gp2, gp3, io1, io2, sc1, or st1. Defaults to gp2.