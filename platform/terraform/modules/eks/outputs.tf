output "cluster_name" {
  description = "EKS cluster name"
  value       = aws_eks_cluster.this.name
}

output "cluster_endpoint" {
  description = "EKS cluster API endpoint"
  value       = aws_eks_cluster.this.endpoint
}

output "cluster_ca_certificate" {
  description = "EKS cluster CA certificate (base64)"
  value       = aws_eks_cluster.this.certificate_authority[0].data
}

output "cluster_auth_token" {
  description = "EKS cluster auth token"
  value       = data.aws_eks_cluster_auth.this.token
  sensitive   = true
}

output "cluster_oidc_issuer" {
  description = "EKS OIDC issuer URL"
  value       = aws_eks_cluster.this.identity[0].oidc[0].issuer
}

output "oidc_provider_arn" {
  description = "OIDC provider ARN (for IRSA)"
  value       = aws_iam_openid_connect_provider.eks.arn
}

output "node_group_name" {
  description = "EKS node group name"
  value       = aws_eks_node_group.workers.node_group_name
}

output "node_group_status" {
  description = "EKS node group status"
  value       = aws_eks_node_group.workers.status
}
