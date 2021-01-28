output "instance_ids" {
  description = "List of instance IDs"
  value       = aws_instance.aion.*.id
}

output "instance_public_ips" {
  description = "List of public IP addresses assigned to the instances, if applicable"
  value       = aws_instance.aion.*.public_ip
}

output "instance_private_ips" {
  description = "List of private IP addresses assigned to the instances, if applicable"
  value       = aws_instance.aion.*.private_ip
}

