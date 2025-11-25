#!/bin/bash
# Скрипт для видалення всіх PARCS instances
# УВАГА: Це видалить instances назавжди!
# Використання: ./delete_instances.sh [zone]

ZONE=${1:-"europe-north1-a"}

echo "=========================================="
echo "УВАГА: Це видалить всі PARCS instances (master, worker1, worker2, worker3)!"
echo "=========================================="
read -p "Ви впевнені? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
  echo "Скасовано."
  exit 0
fi

echo "Видалення PARCS instances в зоні $ZONE..."

# Видалити master
echo "Видалення master..."
gcloud compute instances delete master --zone="$ZONE" --quiet

# Видалити всіх воркерів
for i in 1 2 3; do
  if gcloud compute instances describe "worker$i" --zone="$ZONE" &>/dev/null; then
    echo "Видалення worker$i..."
    gcloud compute instances delete "worker$i" --zone="$ZONE" --quiet
  fi
done

echo "Всі instances видалено!"

