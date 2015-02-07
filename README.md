# ifti-proxy

This is LBaaS driver for HAProxy load balancer running on a stand-alone server or a VM. To use this
place this code in the "neutron/services/loadbalancer/drivers/" directory and place below in the neutron.conf

service_provider=LOADBALANCER:ifti_proxy:neutron.services.loadbalancer.drivers.ifti_proxy.ifti_proxy_driver.IftiPluginDriver

[ifti_proxy_driver]
proxy_hostname="192.168.15.56"
proxy_username="root"
proxy_password="plumgrid"


This is initial release creating and deleting works, need to add update functionallity.

