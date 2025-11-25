#!/bin/bash
# Скрипт для перегляду всіх VM-екземплярів у Google Cloud
# Використання: ./list_instances.sh [zone]

ZONE=${1:-"europe-north1-a"}

echo "=== Список VM-екземплярів у зоні $ZONE ==="
echo ""

# Показати всі instances у вказаній зоні
gcloud compute instances list --zones="$ZONE" --format="table(
    name,
    zone,
    machineType.scope(machineTypes):label=MACHINE_TYPE,
    status,
    internalIP:label=INTERNAL_IP,
    externalIP:label=EXTERNAL_IP
)"

echo ""
echo "=== Детальна інформація про конкретний instance ==="
echo "Для перегляду деталей використайте:"
echo "  gcloud compute instances describe <instance-name> --zone=$ZONE"
echo ""
echo "=== Статус всіх instances у проекті ==="
gcloud compute instances list

