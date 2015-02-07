# Copyright 2015 Iftikhar Rathore
#

#import requests
import paramiko
import time

from neutron.common import exceptions as n_exc
from neutron.openstack.common import log as logging

LOG = logging.getLogger(__name__)

POOLS = "/usr/local/etc/pools/"
class ProxyException(n_exc.NeutronException):

    """Represents exceptions thrown by proxy."""

    CONNECTION_ERROR = 1
    UNKNOWN_ERROR = 2
    EXIST_ERROR = 3
    NOEXIST_ERROR = 4

    def __init__(self, error):
        self.message = _("Proxy Error %d") % error
        super(ProxyException, self).__init__()
        self.error = error


class proxy_helper(object):

    """Client to connect ro HAproxy."""

    def __init__(self, hostname, username, password):
        if not hostname:
            msg = _("No proxy hostname. "
                    "Cannot connect.")
            LOG.exception(msg)
            raise ProxyException(ProxyException.CONNECTION_ERROR)
        self.hostname = hostname
        self.username = username
        self.password = password
        self.transport = paramiko.Transport(hostname)
        self.transport.connect(username=username, password=password)
        self.sftp_client = self.transport.open_sftp_client()
        self.transport.close()


    def proxy_create_pool(self,pool):
       """Create a  pool."""
       msg = _("proxy_create_pool pool=%s") % pool
       LOG.warning(msg)
       filename = POOLS + pool['id']
       self._createfile(filename)   
          

    def proxy_delete_pool(self,pool):
       """Delete a  pool."""
       msg = _("proxy_create_pool pool=%s") % pool
       LOG.warning(msg)
       filename = POOLS + pool['id']
       self._delfile(filename)

    def proxy_create_member(self,member):
       """Create a  Member."""
       pool = member['pool_id']
       port = member['protocol_port']
       filename = POOLS + pool
       address = member['address']
       line = "        server %s %s:%s weight %s \n" % (member['id'], address, port, member['weight'])
       self._addline(line,filename) 
       msg = _("proxy_create_member pool = %s, port = %s, addres = %s") % (pool, port,address)
       LOG.warning(msg)

    def proxy_create_vip(self,vip):
       """Create a  Member."""
       pool = vip['pool_id']
       port = vip['protocol_port']
       filename = POOLS + pool
       address = vip['address']
       line = "        bind %s:%s\n" % (address, port)
       self._addline(line,filename)
       msg = _("proxy_create_vip pool = %s, port = %s, addres = %s") % (pool, port,address)
       LOG.warning(msg)
       self._create_vip_if(vip['name'],address,pool)

    def proxy_delete_vip(self,vip):
       """delete a  vip."""
       pool = vip['pool_id']
       port = vip['protocol_port']
       filename = POOLS + pool
       address = vip['address']
       line = "        bind %s:%s\n" % (address, port)
#       self._addline(line,filename)
       msg = _("proxy_delete_vip pool = %s, port = %s, addres = %s") % (pool, port,address)
       LOG.warning(msg)
       self._delete_vip_if(vip['name'],pool)


    def _delfile(self,path):
       self.transport = paramiko.Transport(self.hostname)
       self.transport.connect(username=self.username, password=self.password)
       self.sftp_client = self.transport.open_sftp_client()

       try:
          my_file = self.sftp_client.stat(path)
       except IOError:
          msg = _("file does not exist %s") % path
          LOG.warning(msg)
          self.transport.close()
          raise ProxyException(ProxyException.NOEXIST_ERROR)

       myfile = self.sftp_client.remove(path)
       self.transport.close()

    def _addline(self,line,path):
       self.transport = paramiko.Transport(self.hostname)
       self.transport.connect(username=self.username, password=self.password)
       self.sftp_client = self.transport.open_sftp_client()

       try:
          my_file = self.sftp_client.stat(path)
       except IOError:
          msg = _("file does not exist %s") % path
          LOG.warning(msg)
          self.transport.close()
          raise ProxyException(ProxyException.NOEXIST_ERROR)

       myfile = self.sftp_client.open(path, 'r')
       lines = myfile.read()
       myfile.close() 
       lines = lines + line
       myfile = self.sftp_client.open(path, 'w')
       myfile.write(lines )
       myfile.close() 
       self.transport.close()

    def _putfile(self,path):
       self.transport = paramiko.Transport(self.hostname)
       self.transport.connect(username=self.username, password=self.password)
       self.sftp_client = self.transport.open_sftp_client()

       try:
          my_file = self.sftp_client.stat(path)
       except IOError:
          my_file = None
       if (my_file != None):
          msg = _("already exists %s") % path
          LOG.warning(msg)
          self.transport.close()
          raise ProxyException(ProxyException.EXIST_ERROR)
       else:
          myfile = self.sftp_client.open(path, 'w')
          myfile.close()
          self.transport.close()


    def _createfile(self,path):
       sourcepath="/etc/haproxy/haproxy.template"
       transport = paramiko.Transport(self.hostname)
       transport.connect(username=self.username, password=self.password)
       sftp_client =transport.open_sftp_client()

       try:
          my_file = sftp_client.stat(path)
       except IOError:
          my_file = None
       if (my_file != None):
          msg = _("already exists %s") % path
          LOG.warning(msg)
          transport.close()
          raise ProxyException(ProxyException.EXIST_ERROR)
       else:
          myfile = sftp_client.open(sourcepath, 'r')
          data = myfile.read()
          myfile.close()
          myfile = sftp_client.open(path, 'w')
          myfile.write(data)
          myfile.close()
          transport.close()


    def _create_vip_if(self,name,address,pool):
       sshclient = paramiko.SSHClient()
       sshclient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
       sshclient.connect(self.hostname,username=self.username, password=self.password)
       sshclient.exec_command("ifconfig eth1:%s %s netmask 255.255.255.0" %(name,address)) 
       time.sleep(1)
       stdin,stdout,stderror = sshclient.exec_command("haproxy -D -f /usr/local/etc/pools/%s -p /tmp/%s" %(pool,pool)) 
       msg = _("haproxy -D -f /usr/local/etc/pools/%s -p /tmp/%s") %(pool,pool)
       LOG.warning(msg)
       msg = _("out = %s, error = %s") % (stdout.readline(), stderror.readline())
       LOG.warning(msg)
       sshclient.close()

    def _delete_vip_if(self,name,pool):
       sshclient = paramiko.SSHClient()
       sshclient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
       sshclient.connect(self.hostname,username=self.username, password=self.password)
       sshclient.exec_command("ifconfig eth1:%s down" % name)
       sshclient.exec_command("pkill -F /tmp/%s" % pool)
       sshclient.exec_command("rm -f /tmp/%s" % pool)
       sshclient.close()

