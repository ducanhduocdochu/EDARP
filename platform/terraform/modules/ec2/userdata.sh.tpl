#!/bin/bash
set -euo pipefail

# ─── Install Docker ──────────────────────────────────────────────────────────
dnf update -y
dnf install -y docker
systemctl enable docker
systemctl start docker

# ─── Mount data volume ───────────────────────────────────────────────────────
DATA_DEVICE="${data_device}"
DATA_MOUNT="${data_mount}"

if ! blkid "$DATA_DEVICE"; then
  mkfs.xfs "$DATA_DEVICE"
fi

mkdir -p "$DATA_MOUNT"
mount "$DATA_DEVICE" "$DATA_MOUNT"

if ! grep -q "$DATA_DEVICE" /etc/fstab; then
  UUID=$(blkid -s UUID -o value "$DATA_DEVICE")
  echo "UUID=$UUID $DATA_MOUNT xfs defaults,nofail 0 2" >> /etc/fstab
fi

chown 1000:1000 "$DATA_MOUNT"

# ─── Run Weaviate ────────────────────────────────────────────────────────────
docker run -d \
  --name weaviate \
  --restart unless-stopped \
  -p ${weaviate_port}:8080 \
  -p ${grpc_port}:50051 \
  -v "$DATA_MOUNT":/var/lib/weaviate \
  -e QUERY_DEFAULTS_LIMIT=25 \
  -e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true \
  -e PERSISTENCE_DATA_PATH=/var/lib/weaviate \
  -e DEFAULT_VECTORIZER_MODULE=none \
  -e CLUSTER_HOSTNAME=node1 \
  -e ENABLE_MODULES="" \
  -e LOG_LEVEL=info \
  -e LIMIT_RESOURCES=false \
  cr.weaviate.io/semitechnologies/weaviate:${weaviate_version}
