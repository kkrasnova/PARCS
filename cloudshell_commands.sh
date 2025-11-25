#!/bin/bash
# Команды для выполнения в Google Cloud Shell

ZONE="europe-north1-a"

echo "=== Перезапуск всех PARCS инстансов ==="
echo ""

# 1. Остановка всех инстансов
echo "1. Остановка инстансов..."
gcloud compute instances stop master worker1 worker2 worker3 --zone=$ZONE

echo ""
echo "Ожидание 20 секунд..."
sleep 20

# 2. Запуск всех инстансов
echo ""
echo "2. Запуск инстансов..."
gcloud compute instances start master worker1 worker2 worker3 --zone=$ZONE

echo ""
echo "Ожидание 40 секунд..."
sleep 40

# 3. Проверка статуса
echo ""
echo "3. Проверка статуса..."
gcloud compute instances list --zones=$ZONE --format="table(name,zone,status,internalIP,externalIP)"

# 4. Получение IP master
echo ""
echo "4. Информация о master..."
MASTER_IP=$(gcloud compute instances describe master --zone=$ZONE --format="get(networkInterfaces[0].accessConfigs[0].natIP)")
echo ""
echo "Веб-интерфейс PARCS: http://$MASTER_IP:8080"

