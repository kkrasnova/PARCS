#!/bin/bash
# Скрипт для запуску всіх PARCS instances у Google Cloud
# Використання: ./start_instances.sh [zone]
#
# За замовчуванням використовується зона europe-north1-a,
# як у методичці до лабораторної.

ZONE=${1:-"europe-north1-a"}

echo "Запуск PARCS instances в зоні $ZONE..."

# Запустити master (instance з іменем 'master')
echo "Запуск master..."
gcloud compute instances start master --zone="$ZONE"

# Запустити всіх воркерів (worker1, worker2, worker3)
for i in 1 2 3; do
  if gcloud compute instances describe "worker$i" --zone="$ZONE" &>/dev/null; then
    echo "Запуск worker$i..."
    gcloud compute instances start "worker$i" --zone="$ZONE"
  else
    echo "Попередження: instance worker$i не знайдено в зоні $ZONE"
  fi
done

echo "Очікування готовності instances (30 секунд)..."
sleep 30

echo "Всі доступні instances запущено!"
echo "Перевірити стан можна командою:"
echo "  gcloud compute instances list --zones=$ZONE"

