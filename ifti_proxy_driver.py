# Copyright 2015 Iftikhar Rathore
#

from oslo.config import cfg

from neutron.api.v2 import attributes
from neutron.db.loadbalancer import loadbalancer_db
from neutron.openstack.common import log as logging
from neutron.plugins.common import constants
from neutron.services.loadbalancer.drivers import abstract_driver
from neutron.services.loadbalancer.drivers.ifti_proxy import proxy_helper

LOG = logging.getLogger(__name__)

IFTI_OPTS = [
    cfg.StrOpt(
        'proxy_hostname',
        help=_('HAProxy Host Name'),
    ),
    cfg.StrOpt(
        'proxy_username',
        help=_('Username to login to the HAProxy server.'),
    ),
    cfg.StrOpt(
        'proxy_password',
        help=_('Password to login to the HAProxy server..'),
    )
]

cfg.CONF.register_opts(IFTI_OPTS, 'ifti_proxy_driver')

DRIVER_NAME = 'ifti_proxy_driver'


class IftiPluginDriver(abstract_driver.LoadBalancerAbstractDriver):

    """proxy class driver"""

    def __init__(self, plugin):
        self.plugin = plugin
        proxy_hostname = cfg.CONF.ifti_proxy_driver.proxy_hostname
        proxy_username = cfg.CONF.ifti_proxy_driver.proxy_username
        proxy_password = cfg.CONF.ifti_proxy_driver.proxy_password
        msg = _("Ifti_Proxy init : %s : %s : %s ") % (proxy_hostname, proxy_username, proxy_password)
        LOG.warning(msg)
        self.client = proxy_helper.proxy_helper(proxy_hostname,
                                          proxy_username,
                                          proxy_password)


    def create_member(self, context, member):
        msg = _("Creating member %s") % member
        LOG.warning(msg)
        self.client.proxy_create_member(member)
        status=constants.ACTIVE
        self.plugin.update_status(context, loadbalancer_db.Member,
                                  member["id"], status)

    def update_member(self, context, old_member, member):
        msg = "Updating member"
        LOG.warning(msg)

    def delete_member(self, context, member):
        msg = "Deleting member"
        LOG.warning(msg)
        self.plugin._delete_db_member(context, member['id'])

    def create_pool(self, context, pool):
        msg = _("Creating pool %s") % pool
        LOG.warning(msg)
        self.client.proxy_create_pool(pool)
        status = constants.ACTIVE
        self.plugin.update_status(context, loadbalancer_db.Pool,
                                  pool['id'], status)

    def update_pool(self, context, old_pool, pool):
        msg = "Updating pool"
        LOG.warning(msg)

    def delete_pool(self, context, pool):
        msg = _("deleting pool %s") % pool
        LOG.warning(msg)
        self.client.proxy_delete_pool(pool)
        self.plugin._delete_db_pool(context, pool['id'])

    def create_pool_health_monitor(self, context, health_monitor, pool_id):
        msg = "Creating pool health"
        LOG.warning(msg)

    def update_pool_health_monitor(self, context, old_health_monitor,
        health_monitor, pool_id):
        msg = "Updating pool health"
        LOG.warning(msg)

    def delete_pool_health_monitor(self, context, health_monitor, pool_id):
        msg = "Deleting pool health"
        LOG.warning(msg)

    def create_vip(self, context, vip):
        msg = _("Creating VIP %s") % vip
        LOG.warning(msg)
        self.client.proxy_create_vip(vip)
        status = constants.ACTIVE
        self.plugin.update_status(context, loadbalancer_db.Vip, vip["id"],
                                  status)
        

    def update_vip(self, context, old_vip, vip):
        msg = "Updating VIP"
        LOG.warning(msg)

    def delete_vip(self, context, vip):
        msg = _("Deleting VIP %s") % vip
        LOG.warning(msg)
        self.client.proxy_delete_vip(vip)
        self.plugin._delete_db_vip(context, vip['id'])

    def stats(self, context, pool_id):
        msg = "stats"
        LOG.warning(msg)

