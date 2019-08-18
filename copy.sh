POD_ID=$1
kubectl cp diskover_crawlftp.py $POD_ID:/diskover/diskover_crawlftp.py
kubectl cp diskover.py $POD_ID:/diskover/diskover.py
kubectl cp diskover_ftpclient.py $POD_ID:/diskover/diskover_ftpclient.py
