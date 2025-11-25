#!/bin/bash
# Скрипт для зупинки всіх PARCS instances у Google Cloud
# Використання: ./stop_instances.sh [zone]

ZONE=${1:-"europe-north1-a"}

echo "Зупинка PARCS instances в зоні $ZONE..."

# Зупинити master
echo "Зупинка master..."
gcloud compute instances stop master --zone="$ZONE"

# Зупинити всіх воркерів
for i in 1 2 3; do
  if gcloud compute instances describe "worker$i" --zone="$ZONE" &>/dev/null; then
    echo "Зупинка worker$i..."
    gcloud compute instances stop "worker$i" --zone="$ZONE"
  fi
done

echo "Всі доступні instances зупинено!"
echo "Для запуску використайте: ./start_instances.sh"

