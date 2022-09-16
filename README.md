# Dashboard_NSO_Docker

This docker-compose file has 4 containers:

- Ubuntu - Where is executed the python script.
- Grafana - It already has a basic dashboard 
- Influxdb - DB that is used by Grafana to get the information
- Mongodb - DB where is stored the network-audit and ptrace information


To start these containers just need to excute:

docker-compose up --build


