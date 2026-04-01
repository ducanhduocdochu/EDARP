output "kms_key_arn" {
  description = "KMS key ARN for encryption"
  value       = aws_kms_key.main.arn
}

output "kms_key_id" {
  description = "KMS key ID"
  value       = aws_kms_key.main.key_id
}

output "eks_cluster_role_arn" {
  description = "IAM role ARN for EKS cluster"
  value       = aws_iam_role.eks_cluster.arn
}

output "eks_node_role_arn" {
  description = "IAM role ARN for EKS node group"
  value       = aws_iam_role.eks_node.arn
}

output "alb_controller_role_arn" {
  description = "IAM role ARN for ALB controller"
  value       = aws_iam_role.alb_controller.arn
}

output "eks_security_group_id" {
  description = "Security group ID for EKS cluster"
  value       = aws_security_group.eks.id
}

output "rds_security_group_id" {
  description = "Security group ID for RDS"
  value       = aws_security_group.rds.id
}

output "alb_security_group_id" {
  description = "Security group ID for ALB"
  value       = aws_security_group.alb.id
}

output "weaviate_security_group_id" {
  description = "Security group ID for Weaviate EC2"
  value       = aws_security_group.weaviate.id
}
