# huawei-rebooter

My Huawei CPE Pro 5G router can be unreliable. Sometimes latency skyrockets and bandwidth gets crappy.

Generally a reboot fixes this. This script automatically reboots the router when ran. I use a cron to run this when 
I'm asleep.

# Build + Push

Build and push to my private docker registry.

```bash
docker buildx build --tag "oscarvanl/dockerhub:huawei-rebooter" .
docker push oscarvanl/dockerhub:huawei-rebooter
```

# Run

```bash
docker run --name huawei-rebooter -e ROUTER_IP=192.168.0.1 -e ROUTER_USER=admin -e ROUTER_PASS=<PASSWORD> oscarvanl/dockerhub:huawei-rebooter
```
