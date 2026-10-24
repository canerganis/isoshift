#!/usr/bin/env bash
# Log GPU temperature, power and clocks once a minute while P12 jobs run (diagnosis of the 04:16 shutdown).
cd "$(dirname "$0")/../.."
while true; do
  echo "$(date '+%F %T'),$(nvidia-smi --query-gpu=temperature.gpu,power.draw,clocks.gr,utilization.gpu,memory.used --format=csv,noheader,nounits)" >> results/pimd/logs/thermal.csv
  sleep 60
done
