output "instance_id" {
  description = "Weaviate EC2 instance ID"
  value       = aws_instance.weaviate.id
}

output "private_ip" {
  description = "Weaviate EC2 private IP"
  value       = aws_instance.weaviate.private_ip
}

output "private_dns" {
  description = "Weaviate EC2 private DNS"
  value       = aws_instance.weaviate.private_dns
}

output "weaviate_endpoint" {
  description = "Weaviate HTTP endpoint (internal)"
  value       = "http://${aws_instance.weaviate.private_ip}:${var.weaviate_port}"
}

output "weaviate_grpc_endpoint" {
  description = "Weaviate gRPC endpoint (internal)"
  value       = "${aws_instance.weaviate.private_ip}:${var.weaviate_grpc_port}"
}

output "data_volume_id" {
  description = "EBS data volume ID"
  value       = aws_ebs_volume.weaviate_data.id
}
