#!/bin/bash
# Команды для получения информации о PARCS в Cloud Shell

ZONE="europe-north1-a"

echo "=== Информация о PARCS инстансах ==="
echo ""

# Полная информация о всех инстансах
echo "1. Детальная информация о всех инстансах:"
gcloud compute instances list --zones=$ZONE --format="table(name,zone,status,networkInterfaces[0].networkIP:label=INTERNAL_IP,networkInterfaces[0].accessConfigs[0].natIP:label=EXTERNAL_IP)"

echo ""
echo "2. Внешний IP master для веб-интерфейса:"
MASTER_IP=$(gcloud compute instances describe master --zone=$ZONE --format="get(networkInterfaces[0].accessConfigs[0].natIP)")
echo "   http://$MASTER_IP:8080"

echo ""
echo "3. Внутренний IP master (для workers):"
MASTER_INTERNAL=$(gcloud compute instances describe master --zone=$ZONE --format="get(networkInterfaces[0].networkIP)")
echo "   $MASTER_INTERNAL"

echo ""
echo "=== Готово! ==="
echo ""
echo "Откройте веб-интерфейс PARCS:"
echo "  http://$MASTER_IP:8080"
echo ""
echo "Для создания job:"
echo "  1. Загрузите prime_solution.py как Solution File"
echo "  2. Загрузите входной файл (prime_input_10000.txt и т.д.)"
echo "  3. Создайте job"

