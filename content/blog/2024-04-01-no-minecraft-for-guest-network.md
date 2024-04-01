<!-- title: No Minecraft for the Guest Network -->
<!-- subtitle: Docker Networking Issues -->

# 2024-04-01 No Minecraft for the Guest Network

## Issue

The initial issue was discovered by my roommate when he could not connect to my local Minecraft server. In my apartment, I have my server network that I only allow myself on, and I have my guest network, which all roommates, guests, and IoT devices get put on. The issue was very strange because I could connect just fine from my server network, and friends outside of my network could connect fine via the Dynamic DNS address I have set up (minecraft.domain.com).

## Troubleshooting

I spent wayyy too much time troubleshooting the router and implementing configurations that either did nothing or had negative effects. I made a lot of static routes, traffic rules (allow rules), policy-based routes, messed with ad blocking, multicast DNS, DNS shielding, country restrictions, and VLAN rules. The country restrictions actually caused me issues with a tool that I use for a class that simplifies writing penetration testing reports.

I finally was convinced it was not a router issue when I was running a `tcpdump` on the Docker VM and noticed traffic was reaching the server. This led me to do some searching for traffic not being able to be routed from different subnets/VLANs to Docker servers.

## Networking

I found this [reddit thread](https://www.reddit.com/r/docker/comments/154bsz7/comment/jssyw27/?context=8&depth=9) that explained a similar issue, which led me to the [Docker docs](https://docs.docker.com/network/drivers/bridge/#use-the-default-bridge-network) and I figured out the issue. Upon running `ip addr` on my Docker host (which showed many networks), I saw the bridge interface with the network of 192.168.0.1/20. I figured this was why my traffic was not being routed properly, and I figured a really easy fix would be to change the IP address scheme of my guest network. My final test was to run `ip link delete {{ name of docker bridge network interface }}` and I tested the Minecraft server, which finally connected. 

However, when checking my Uptime Kuma instance, I noticed that some containers were reporting as down. I went back to my Docker host and restarted the docker service with `systemctl restart docker`, which successfully recreated the bridge network. I believe this change came about as a result of my normal homelab experimentation and creating new services, as the containers I set up just a week ago were the only ones brought down by deleting the default bridge interface on the docker host.

## Unifi changes

I wanted to isolate traffic from my main server network and my guest network, so I enabled traffic isolation in 

`Settings > {{ network name }} > Isolate Network`

However, this caused the guest network to not be able to reach the server again. I created an allow rule in the firewall to allow traffic to reach the Minecraft server

`Settings > Traffic and Firewall Rules > Allow Minecraft`

```markdown
- Action: Allow
- Source: {{ guest network name }} 
- Destination: IP address
- {{ IP address and port of MC server }}
- Schedule: Always
```

This resolved the issue while still keeping the rest of the server network separated. 

## TLDR

- Guest network traffic not routable to Minecraft server
- Docker default network - 192.168.0.1/20
- Guest network - 192.168.1.1/24
- Guest network traffic reaching docker server, but not being routed back out to network
  - instead return traffic destined for Guest network being routed to Docker default bridge network interface
- Resolved by changing Guest network to 192.168.231.1/24
