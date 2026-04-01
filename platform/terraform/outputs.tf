# ─── VPC ──────────────────────────────────────────────────────────────────────
output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}

output "private_subnet_ids" {
  description = "Private subnet IDs"
  value       = module.vpc.private_subnet_ids
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = module.vpc.public_subnet_ids
}

# ─── RDS ──────────────────────────────────────────────────────────────────────
output "rds_auth_endpoint" {
  description = "RDS endpoint for auth_db"
  value       = module.rds.auth_db_endpoint
}

output "rds_project_endpoint" {
  description = "RDS endpoint for project_db"
  value       = module.rds.project_db_endpoint
}

# ─── EKS ──────────────────────────────────────────────────────────────────────
output "eks_cluster_name" {
  description = "EKS cluster name"
  value       = module.eks.cluster_name
}

output "eks_cluster_endpoint" {
  description = "EKS cluster API endpoint"
  value       = module.eks.cluster_endpoint
}

output "eks_oidc_provider_arn" {
  description = "EKS OIDC provider ARN (for IRSA)"
  value       = module.eks.oidc_provider_arn
}

# ─── EC2 (Weaviate) ──────────────────────────────────────────────────────────
output "weaviate_private_ip" {
  description = "Weaviate EC2 private IP"
  value       = module.ec2.private_ip
}

output "weaviate_endpoint" {
  description = "Weaviate HTTP endpoint (internal)"
  value       = module.ec2.weaviate_endpoint
}

output "weaviate_instance_id" {
  description = "Weaviate EC2 instance ID"
  value       = module.ec2.instance_id
}

# ─── S3 ──────────────────────────────────────────────────────────────────────
output "s3_documents_bucket" {
  description = "S3 bucket name for document uploads"
  value       = module.s3.bucket_name
}

output "s3_documents_bucket_arn" {
  description = "S3 bucket ARN"
  value       = module.s3.bucket_arn
}

# ─── SQS ──────────────────────────────────────────────────────────────────────
output "sqs_indexing_queue_url" {
  description = "SQS queue URL for indexing tasks"
  value       = module.sqs.queue_url
}

output "sqs_indexing_queue_arn" {
  description = "SQS queue ARN"
  value       = module.sqs.queue_arn
}
