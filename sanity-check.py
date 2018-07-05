#!/usr/bin/env python
# Ensures that every Gerrit project is configured in Gerrit replication,
# Zuul layout and Gerritbot.

from __future__ import print_function

import collections
import glob
import json
import re
import requests
import sys
import yaml
from six.moves import configparser, StringIO

GERRIT = "https://review.rdoproject.org/r/"
PROJECT_LIST = GERRIT + "/projects/"
# Note (dmsimard): centos-opstools might be sent to #centos-devel,
#                  need to verify with them first.
IGNORED_PROJECTS = {
    'replication': [
        'All-Users',
        'gating_scripts',
        'openstack/whitebox-tempest-plugin',
        'rdo',
        'rdo_gating_scripts',
        'testbranching',
        'testproject'
    ],
    'zuul': [
        'All-Users',
        'config',
        'gating_scripts',
        'rdo',
        'rdo_gating_scripts',
        'centos-opstools/opstools-ansible',
        'rdo-infra/ansible-role-logserver',
        'rdo-infra/ansible-role-rdo-base',
        'rdo-infra/ansible-role-rdo-bot',
        'rdo-infra/ansible-role-rdo-kolla-build',
        'rdo-infra/ansible-role-rdo_dashboards',
        'rdo-infra/ansible-role-rdomonitoring',
        'rdo-infra/ansible-role-weirdo-common',
        'rdo-infra/ansible-role-weirdo-kolla',
        'rdo-infra/ansible-role-weirdo-logs',
        'rdo-infra/ansible-role-weirdo-packstack',
        'rdo-infra/ansible-role-weirdo-puppet-openstack',
        'rdo-infra/rdo-infra-playbooks',
        'rdo-infra/weirdo',
        'rdo-jobs',
        'testbranching',
        'testproject',
        'centos-opstools/kibana',
        'rdo-infra/centos-release-openstack',
        'rdo-infra/example-distgit',
        'rdo-infra/rdo-dashboards',
        'rdo-infra/rdo-release',
        'rdo-infra/rdobot',
        'rdo-infra/test-day-tools',
        'rdo-infra/puppet-dlrn',
        'rdo-infra/rdo-container-registry',
        'rdo-infra/releng',
        'openstack/ansible-pacemaker',
        'openstack/ansible-role-container-registry',
        'openstack/ansible-role-redhat-subscription',
        'openstack/ansible-role-tripleo-modify-image',
        'openstack/aodh',
        'openstack/aodhclient',
        'openstack/app-catalog-ui',
        'openstack/automaton',
        'openstack/barbican',
        'openstack/barbicanclient',
        'openstack/barbican-tempest-plugin',
        'openstack/castellan',
        'openstack/ceilometer',
        'openstack/ceilometerclient',
        'openstack/ceilometermiddleware',
        'openstack/cinder',
        'openstack/cinderclient',
        'openstack/cinder-tempest-plugin',
        'openstack/cisco-ironic-contrib',
        'openstack/cliff',
        'openstack/cloudkitty',
        'openstack/cloudkittyclient',
        'openstack/cloudkitty-dashboard',
        'openstack/collectd-ceilometer-plugin',
        'openstack/collectd-gnocchi',
        'openstack/congress',
        'openstack/congressclient',
        'openstack/congress-tempest-plugin',
        'openstack/cursive',
        'openstack/debtcollector',
        'openstack/designate',
        'openstack/designateclient',
        'openstack/designate-dashboard',
        'openstack/designate-tempest-plugin',
        'openstack/django_openstack_auth',
        'openstack/dracclient',
        'openstack/ec2-api',
        'openstack/ec2api-tempest-plugin',
        'openstack/futurist',
        'openstack/glanceclient',
        'openstack/glance_store',
        'openstack/glare',
        'openstack/glareclient',
        'openstack/gnocchi',
        'openstack/gnocchiclient',
        'openstack/hacking',
        'openstack/hardware',
        'openstack/heat-agents',
        'openstack/heatclient',
        'openstack/heat-dashboard',
        'openstack/heat-tempest-plugin',
        'openstack/heat-templates',
        'openstack/heat-translator',
        'openstack/horizon',
        'openstack/ironicclient',
        'openstack/ironic-inspector-client',
        'openstack/ironic-lib',
        'openstack/ironic-staging-drivers',
        'openstack/ironic-tempest-plugin',
        'openstack/ironic-ui',
        'openstack/k8sclient',
        'openstack/karbor',
        'openstack/karborclient',
        'openstack/karbor-dashboard',
        'openstack/keystone',
        'openstack/keystoneauth1',
        'openstack/keystoneclient',
        'openstack/keystonemiddleware',
        'openstack/keystone-tempest-plugin',
        'openstack/kolla',
        'openstack/kuryr',
        'openstack/kuryr-kubernetes',
        'openstack/kuryr-tempest-plugin',
        'openstack/magnum',
        'openstack/magnumclient',
        'openstack/magnum-tempest-plugin',
        'openstack/magnum-ui',
        'openstack/manila',
        'openstack/manilaclient',
        'openstack/manila-tempest-plugin',
        'openstack/manila-ui',
        'openstack/metalsmith',
        'openstack/microversion-parse',
        'openstack/mistralclient',
        'openstack/mistral-dashboard',
        'openstack/mistral-extra',
        'openstack/mistral-lib',
        'openstack/mistral-tempest-plugin',
        'openstack/monascaclient',
        'openstack/mox3',
        'openstack/murano',
        'openstack/murano-agent',
        'openstack/muranoclient',
        'openstack/murano-dashboard',
        'openstack/murano-tempest-plugin',
        'openstack/networking-ansible',
        'openstack/networking-arista',
        'openstack/networking-bagpipe',
        'openstack/networking-baremetal',
        'openstack/networking-bgpvpn',
        'openstack/networking-bigswitch',
        'openstack/networking-cisco',
        'openstack/networking-fujitsu',
        'openstack/networking-generic-switch',
        'openstack/networking-l2gw',
        'openstack/networking-l2gw-tempest-plugin',
        'openstack/networking-mlnx',
        'openstack/networking-odl',
        'openstack/networking-ovn',
        'openstack/networking-sfc',
        'openstack/networking-vsphere',
        'openstack/neutronclient',
        'openstack/neutron-dynamic-routing',
        'openstack/neutron-fwaas',
        'openstack/neutron-lbaas',
        'openstack/neutron-lbaas-dashboard',
        'openstack/neutron-lib',
        'openstack/neutron-tempest-plugin',
        'openstack/neutron-vpnaas',
        'openstack/novaclient',
        'openstack/novajoin',
        'openstack/novajoin-tempest-plugin',
        'openstack/octavia',
        'openstack/octaviaclient',
        'openstack/octavia-dashboard',
        'openstack/octavia-tempest-plugin',
        'openstack/openstackclient',
        'openstack/openstack-macros',
        'openstack/openstack-puppet-modules',
        'openstack/openstacksdk',
        'openstack/openstack-selinux',
        'openstack/os-brick',
        'openstack/osc-lib',
        'openstack/os-client-config',
        'openstack/os-cloud-config',
        'openstack/os-faults',
        'openstack/oslo-cache',
        'openstack/oslo-concurrency',
        'openstack/oslo-config',
        'openstack/oslo-context',
        'openstack/oslo-db',
        'openstack/oslo-i18n',
        'openstack/oslo-log',
        'openstack/oslo-messaging',
        'openstack/oslo-middleware',
        'openstack/oslo-policy',
        'openstack/oslo-privsep',
        'openstack/oslo-reports',
        'openstack/oslo-rootwrap',
        'openstack/oslo-serialization',
        'openstack/oslo-service',
        'openstack/oslo-sphinx',
        'openstack/oslotest',
        'openstack/oslo-utils',
        'openstack/oslo-versionedobjects',
        'openstack/oslo-vmware',
        'openstack/osops-tools-monitoring-oschecks',
        'openstack/osprofiler',
        'openstack/os-service-types',
        'openstack/os-testr',
        'openstack/os-traits',
        'openstack/os-vif',
        'openstack/os-win',
        'openstack/oswin-tempest-plugin',
        'openstack/os-xenapi',
        'openstack/ovsdbapp',
        'openstack/packstack',
        'openstack/panko',
        'openstack/pankoclient',
        'openstack/patrole',
        'openstack/proliantutils',
        'openstack/pycadf',
        'openstack/rally',
        'openstack/reno',
        'openstack/requestsexceptions',
        'openstack/rsdclient',
        'openstack/rsd-lib',
        'openstack/sahara',
        'openstack/saharaclient',
        'openstack/sahara-dashboard',
        'openstack/sahara-image-elements',
        'openstack/sahara-tests',
        'openstack/scciclient',
        'openstack/senlin',
        'openstack/senlinclient',
        'openstack/shade',
        'openstack/shaker',
        'openstack/stevedore',
        'openstack/sushy',
        'openstack/swift',
        'openstack/swift3',
        'openstack/swiftclient',
        'openstack/tacker',
        'openstack/tackerclient',
        'openstack/tap-as-a-service',
        'openstack/taskflow',
        'openstack/telemetry-tempest-plugin',
        'openstack/tempestconf',
        'openstack/tempest-horizon',
        'openstack/tempest-lib',
        'openstack/tooz',
        'openstack/tripleoclient',
        'openstack/tripleo-common-tempest-plugin',
        'openstack/tripleo-incubator',
        'openstack/tripleo-repos',
        'openstack/tripleo-ui',
        'openstack/tripleo-validations',
        'openstack/trove',
        'openstack/troveclient',
        'openstack/trove-dashboard',
        'openstack/trove-tempest-plugin',
        'openstack/UcsSdk',
        'openstack/virtualbmc',
        'openstack/vitrage',
        'openstack/vitrageclient',
        'openstack/vitrage-dashboard',
        'openstack/vitrage-tempest-plugin',
        'openstack/vmware-nsx',
        'openstack/vmware-nsxlib',
        'openstack/vmware-nsx-tempest-plugin',
        'openstack/watcher',
        'openstack/watcher-tempest-plugin',
        'openstack/wsme',
        'openstack/zaqar',
        'openstack/zaqarclient',
        'openstack/zaqar-tempest-plugin',
        'puppet/puppet-aodh',
        'puppet/puppet-apache',
        'puppet/puppet-archive',
        'puppet/puppet-auditd',
        'puppet/puppet-barbican',
        'puppet/puppet-cassandra',
        'puppet/puppet-ceilometer',
        'puppet/puppet-ceph',
        'puppet/puppet-certmonger',
        'puppet/puppet-cinder',
        'puppet/puppet-collectd',
        'puppet/puppet-concat',
        'puppet/puppet-congress',
        'puppet/puppet-contrail',
        'puppet/puppet-corosync',
        'puppet/puppet-datacat',
        'puppet/puppet-designate',
        'puppet/puppet-dns',
        'puppet/puppet-ec2api',
        'puppet/puppet-elasticsearch',
        'puppet/puppet-etcd',
        'puppet/puppet-fdio',
        'puppet/puppet-firewall',
        'puppet/puppet-fluentd',
        'puppet/puppet-git',
        'puppet/puppet-glance',
        'puppet/puppet-gnocchi',
        'puppet/puppet-haproxy',
        'puppet/puppet-heat',
        'puppet/puppet-horizon',
        'puppet/puppet-inifile',
        'puppet/puppet-ipaclient',
        'puppet/puppet-ironic',
        'puppet/puppet-java',
        'puppet/puppet-kafka',
        'puppet/puppet-keepalived',
        'puppet/puppet-keystone',
        'puppet/puppet-kibana3',
        'puppet/puppet-kmod',
        'puppet/puppet-lib-file_concat',
        'puppet/puppet-logstash',
        'puppet/puppet-magnum',
        'puppet/puppet-manila',
        'puppet/puppet-memcached',
        'puppet/puppet-midonet',
        'puppet/puppet-midonet_openstack',
        'puppet/puppet-mistral',
        'puppet/puppet-module-data',
        'puppet/puppet-mongodb',
        'puppet/puppet-murano',
        'puppet/puppet-mysql',
        'puppet/puppet-n1k-vsm',
        'puppet/puppet-neutron',
        'puppet/puppet-nova',
        'puppet/puppet-nssdb',
        'puppet/puppet-ntp',
        'puppet/puppet-octavia',
        'puppet/puppet-opendaylight',
        'puppet/puppet-openstack_extras',
        'puppet/puppet-openstacklib',
        'puppet/puppet-oslo',
        'puppet/puppet-ovn',
        'puppet/puppet-pacemaker',
        'puppet/puppet-panko',
        'puppet/puppet-powerdns',
        'puppet/puppet-qdr',
        'puppet/puppet-rabbitmq',
        'puppet/puppet-redis',
        'puppet/puppet-remote',
        'puppet/puppet-rsync',
        'puppet/puppet-sahara',
        'puppet/puppet-sensu',
        'puppet/puppet-snmp',
        'puppet/puppet-ssh',
        'puppet/puppet-staging',
        'puppet/puppet-stdlib',
        'puppet/puppet-swift',
        'puppet/puppet-sysctl',
        'puppet/puppet-systemd',
        'puppet/puppet-tacker',
        'puppet/puppet-tempest',
        'puppet/puppet-timezone',
        'puppet/puppet-tomcat',
        'puppet/puppet-trove',
        'puppet/puppet-uchiwa',
        'puppet/puppet-vcsrepo',
        'puppet/puppet-veritas_hyperscale',
        'puppet/puppet-vitrage',
        'puppet/puppet-vlan',
        'puppet/puppet-vswitch',
        'puppet/puppet-xinetd',
        'puppet/puppet-zaqar',
        'puppet/puppet-zookeeper',
        'openstack/ansible-pacemaker-distgit',
        'openstack/ansible-role-container-registry-distgit',
        'openstack/ansible-role-redhat-subscription-distgit',
        'openstack/ansible-role-tripleo-modify-image-distgit',
        'openstack/app-catalog-ui-distgit',
        'openstack/automaton-distgit',
        'openstack/barbican-tempest-plugin-distgit',
        'openstack/castellan-distgit',
        'openstack/cinder-tempest-plugin-distgit',
        'openstack/cisco-ironic-contrib-distgit',
        'openstack/cliff-distgit',
        'openstack/cloudkittyclient-distgit',
        'openstack/cloudkitty-dashboard-distgit',
        'openstack/cloudkitty-distgit',
        'openstack/collectd-ceilometer-plugin-distgit',
        'openstack/collectd-gnocchi-distgit',
        'openstack/congressclient-distgit',
        'openstack/congress-distgit',
        'openstack/congress-tempest-plugin-distgit',
        'openstack/cursive-distgit',
        'openstack/debtcollector-distgit',
        'openstack/designateclient-distgit',
        'openstack/designate-dashboard-distgit',
        'openstack/designate-distgit',
        'openstack/designate-tempest-plugin-distgit',
        'openstack/dib-utils-distgit',
        'openstack/diskimage-builder-distgit',
        'openstack/django_openstack_auth-distgit',
        'openstack/dracclient-distgit',
        'openstack/ec2-api-distgit',
        'openstack/ec2api-tempest-plugin-distgit',
        'openstack/futurist-distgit',
        'openstack/glareclient-distgit',
        'openstack/glare-distgit',
        'openstack/hacking-distgit',
        'openstack/hardware-distgit',
        'openstack/heat-agents-distgit',
        'openstack/heat-dashboard-distgit',
        'openstack/heat-tempest-plugin-distgit',
        'openstack/heat-translator-distgit',
        'openstack/instack-distgit',
        'openstack/instack-undercloud-distgit',
        'openstack/ironicclient-distgit',
        'openstack/ironic-distgit',
        'openstack/ironic-inspector-client-distgit',
        'openstack/ironic-inspector-distgit',
        'openstack/ironic-lib-distgit',
        'openstack/ironic-python-agent-distgit',
        'openstack/ironic-staging-drivers-distgit',
        'openstack/ironic-tempest-plugin-distgit',
        'openstack/ironic-ui-distgit',
        'openstack/k8sclient-distgit',
        'openstack/karborclient-distgit',
        'openstack/karbor-dashboard-distgit',
        'openstack/karbor-distgit',
        'openstack/keystone-tempest-plugin-distgit',
        'openstack/kolla-distgit',
        'openstack/kuryr-distgit',
        'openstack/kuryr-kubernetes-distgit',
        'openstack/kuryr-tempest-plugin-distgit',
        'openstack/magnumclient-distgit',
        'openstack/magnum-distgit',
        'openstack/magnum-tempest-plugin-distgit',
        'openstack/magnum-ui-distgit',
        'openstack/manilaclient-distgit',
        'openstack/manila-distgit',
        'openstack/manila-tempest-plugin-distgit',
        'openstack/manila-ui-distgit',
        'openstack/metalsmith-distgit',
        'openstack/microversion-parse-distgit',
        'openstack/mistralclient-distgit',
        'openstack/mistral-dashboard-distgit',
        'openstack/mistral-distgit',
        'openstack/mistral-extra-distgit',
        'openstack/mistral-lib-distgit',
        'openstack/mistral-tempest-plugin-distgit',
        'openstack/monascaclient-distgit',
        'openstack/mox3-distgit',
        'openstack/murano-agent-distgit',
        'openstack/muranoclient-distgit',
        'openstack/murano-dashboard-distgit',
        'openstack/murano-distgit',
        'openstack/murano-tempest-plugin-distgit',
        'openstack/networking-ansible-distgit',
        'openstack/networking-arista-distgit',
        'openstack/networking-bagpipe-distgit',
        'openstack/networking-baremetal-distgit',
        'openstack/networking-bigswitch-distgit',
        'openstack/networking-cisco-distgit',
        'openstack/networking-fujitsu-distgit',
        'openstack/networking-generic-switch-distgit',
        'openstack/networking-l2gw-distgit',
        'openstack/networking-l2gw-tempest-plugin-distgit',
        'openstack/networking-mlnx-distgit',
        'openstack/networking-odl-distgit',
        'openstack/networking-ovn-distgit',
        'openstack/networking-sfc-distgit',
        'openstack/networking-vsphere-distgit',
        'openstack/neutron-dynamic-routing-distgit',
        'openstack/neutron-tempest-plugin-distgit',
        'openstack/novajoin-distgit',
        'openstack/novajoin-tempest-plugin-distgit',
        'openstack/octaviaclient-distgit',
        'openstack/octavia-dashboard-distgit',
        'openstack/octavia-distgit',
        'openstack/octavia-tempest-plugin-distgit',
        'openstack/openstack-macros-distgit',
        'openstack/openstack-puppet-modules-distgit',
        'openstack/openstacksdk-distgit',
        'openstack/openstack-selinux-distgit',
        'openstack/os-apply-config-distgit',
        'openstack/os-collect-config-distgit',
        'openstack/os-faults-distgit',
        'openstack/oslo-vmware-distgit',
        'openstack/os-net-config-distgit',
        'openstack/osops-tools-monitoring-oschecks-distgit',
        'openstack/osprofiler-distgit',
        'openstack/os-refresh-config-distgit',
        'openstack/os-service-types-distgit',
        'openstack/os-testr-distgit',
        'openstack/os-traits-distgit',
        'openstack/os-vif-distgit',
        'openstack/os-win-distgit',
        'openstack/oswin-tempest-plugin-distgit',
        'openstack/os-xenapi-distgit',
        'openstack/ovsdbapp-distgit',
        'openstack/packstack-distgit',
        'openstack/pankoclient-distgit',
        'openstack/panko-distgit',
        'openstack/patrole-distgit',
        'openstack/paunch-distgit',
        'openstack/proliantutils-distgit',
        'openstack/rally-distgit',
        'openstack/reno-distgit',
        'openstack/requestsexceptions-distgit',
        'openstack/rsdclient-distgit',
        'openstack/rsd-lib-distgit',
        'openstack/saharaclient-distgit',
        'openstack/sahara-dashboard-distgit',
        'openstack/sahara-distgit',
        'openstack/sahara-image-elements-distgit',
        'openstack/sahara-tests-distgit',
        'openstack/scciclient-distgit',
        'openstack/senlinclient-distgit',
        'openstack/senlin-distgit',
        'openstack/shade-distgit',
        'openstack/shaker-distgit',
        'openstack/sushy-distgit',
        'openstack/swift3-distgit',
        'openstack/swiftclient-distgit',
        'openstack/swift-distgit',
        'openstack/tackerclient-distgit',
        'openstack/tacker-distgit',
        'openstack/tap-as-a-service-distgit',
        'openstack/telemetry-tempest-plugin-distgit',
        'openstack/tempestconf-distgit',
        'openstack/tempest-distgit',
        'openstack/tempest-horizon-distgit',
        'openstack/tempest-lib-distgit',
        'openstack/tooz-distgit',
        'openstack/tripleoclient-distgit',
        'openstack/tripleo-common-distgit',
        'openstack/tripleo-common-tempest-plugin-distgit',
        'openstack/tripleo-heat-templates-compat-distgit',
        'openstack/tripleo-heat-templates-distgit',
        'openstack/tripleo-image-elements-distgit',
        'openstack/tripleo-incubator-distgit',
        'openstack/tripleo-ipsec-distgit',
        'openstack/tripleo-puppet-elements-distgit',
        'openstack/tripleo-repos-distgit',
        'openstack/tripleo-ui-distgit',
        'openstack/tripleo-validations-distgit',
        'openstack/troveclient-distgit',
        'openstack/trove-dashboard-distgit',
        'openstack/trove-distgit',
        'openstack/trove-tempest-plugin-distgit',
        'openstack/UcsSdk-distgit',
        'openstack/virtualbmc-distgit',
        'openstack/vitrageclient-distgit',
        'openstack/vitrage-dashboard-distgit',
        'openstack/vitrage-distgit',
        'openstack/vitrage-tempest-plugin-distgit',
        'openstack/vmware-nsx-distgit',
        'openstack/vmware-nsxlib-distgit',
        'openstack/vmware-nsx-tempest-plugin-distgit',
        'openstack/watcher-tempest-plugin-distgit',
        'openstack/wsme-distgit',
        'openstack/zaqar-tempest-plugin-distgit',
        'puppet/puppet-archive-distgit',
        'puppet/puppet-auditd-distgit',
        'puppet/puppet-barbican-distgit',
        'puppet/puppet-cassandra-distgit',
        'puppet/puppet-certmonger-distgit',
        'puppet/puppet-collectd-distgit',
        'puppet/puppet-congress-distgit',
        'puppet/puppet-contrail-distgit',
        'puppet/puppet-corosync-distgit',
        'puppet/puppet-datacat-distgit',
        'puppet/puppet-designate-distgit',
        'puppet/puppet-dns-distgit',
        'puppet/puppet-ec2api-distgit',
        'puppet/puppet-elasticsearch-distgit',
        'puppet/puppet-etcd-distgit',
        'puppet/puppet-fdio-distgit',
        'puppet/puppet-firewall-distgit',
        'puppet/puppet-fluentd-distgit',
        'puppet/puppet-git-distgit',
        'puppet/puppet-haproxy-distgit',
        'puppet/puppet-horizon-distgit',
        'puppet/puppet-inifile-distgit',
        'puppet/puppet-ipaclient-distgit',
        'puppet/puppet-ironic-distgit',
        'puppet/puppet-java-distgit',
        'puppet/puppet-kafka-distgit',
        'puppet/puppet-keepalived-distgit',
        'puppet/puppet-kibana3-distgit',
        'puppet/puppet-kmod-distgit',
        'puppet/puppet-lib-file_concat-distgit',
        'puppet/puppet-logstash-distgit',
        'puppet/puppet-magnum-distgit',
        'puppet/puppet-manila-distgit',
        'puppet/puppet-memcached-distgit',
        'puppet/puppet-midonet-distgit',
        'puppet/puppet-midonet_openstack-distgit',
        'puppet/puppet-mistral-distgit',
        'puppet/puppet-module-data-distgit',
        'puppet/puppet-murano-distgit',
        'puppet/puppet-n1k-vsm-distgit',
        'puppet/puppet-nssdb-distgit',
        'puppet/puppet-ntp-distgit',
        'puppet/puppet-octavia-distgit',
        'puppet/puppet-opendaylight-distgit',
        'puppet/puppet-ovn-distgit',
        'puppet/puppet-pacemaker-distgit',
        'puppet/puppet-panko-distgit',
        'puppet/puppet-powerdns-distgit',
        'puppet/puppet-qdr-distgit',
        'puppet/puppet-redis-distgit',
        'puppet/puppet-remote-distgit',
        'puppet/puppet-rsync-distgit',
        'puppet/puppet-sahara-distgit',
        'puppet/puppet-sensu-distgit',
        'puppet/puppet-snmp-distgit',
        'puppet/puppet-ssh-distgit',
        'puppet/puppet-staging-distgit',
        'puppet/puppet-swift-distgit',
        'puppet/puppet-systemd-distgit',
        'puppet/puppet-tacker-distgit',
        'puppet/puppet-timezone-distgit',
        'puppet/puppet-tomcat-distgit',
        'puppet/puppet-tripleo-distgit',
        'puppet/puppet-trove-distgit',
        'puppet/puppet-uchiwa-distgit',
        'puppet/puppet-vcsrepo-distgit',
        'puppet/puppet-veritas_hyperscale-distgit',
        'puppet/puppet-vitrage-distgit',
        'puppet/puppet-vlan-distgit',
        'puppet/puppet-vswitch-distgit',
        'puppet/puppet-xinetd-distgit',
        'puppet/puppet-zookeeper-distgit',
        'centos-opstools/centos-release-opstools',
        'centos-opstools/collectd',
        'centos-opstools/fluentd',
        'centos-opstools/intel-cmt-cat',
        'centos-opstools/opstools-ansible-distgit',
        'centos-opstools/osops-tools-monitoring-oschecks',
        'centos-opstools/python-fluent-logger',
        'centos-opstools/rubygem-addressable',
        'centos-opstools/rubygem-aruba',
        'centos-opstools/rubygem-atomic',
        'centos-opstools/rubygem-backports',
        'centos-opstools/rubygem-bacon',
        'centos-opstools/rubygem-builder',
        'centos-opstools/rubygem-childprocess',
        'centos-opstools/rubygem-concurrent-ruby',
        'centos-opstools/rubygem-contracts',
        'centos-opstools/rubygem-cookiejar',
        'centos-opstools/rubygem-cool.io',
        'centos-opstools/rubygem-coveralls',
        'centos-opstools/rubygem-cucumber',
        'centos-opstools/rubygem-cucumber-core',
        'centos-opstools/rubygem-cucumber-wire',
        'centos-opstools/rubygem-diff-lcs',
        'centos-opstools/rubygem-docile',
        'centos-opstools/rubygem-domain_name',
        'centos-opstools/rubygem-elasticsearch',
        'centos-opstools/rubygem-elasticsearch-api',
        'centos-opstools/rubygem-elasticsearch-transport',
        'centos-opstools/rubygem-em-http-request',
        'centos-opstools/rubygem-em-http-server',
        'centos-opstools/rubygem-em-redis-unified',
        'centos-opstools/rubygem-em-socksify',
        'centos-opstools/rubygem-em-worker',
        'centos-opstools/rubygem-eventmachine',
        'centos-opstools/rubygem-excon',
        'centos-opstools/rubygem-fakeweb',
        'centos-opstools/rubygem-faraday',
        'centos-opstools/rubygem-ffi',
        'centos-opstools/rubygem-fluent-plugin-collectd-nest',
        'centos-opstools/rubygem-fluent-plugin-elasticsearch',
        'centos-opstools/rubygem-fluent-plugin-grok-parser',
        'centos-opstools/rubygem-fluent-plugin-kubernetes_metadata_filter',
        'centos-opstools/rubygem-fluent-plugin-rewrite-tag-filter',
        'centos-opstools/rubygem-fluent-plugin-secure-forward',
        'centos-opstools/rubygem-fluent-plugin-viaq_data_model',
        'centos-opstools/rubygem-gherkin',
        'centos-opstools/rubygem-http',
        'centos-opstools/rubygem-http_connection',
        'centos-opstools/rubygem-http-cookie',
        'centos-opstools/rubygem-http-form_data',
        'centos-opstools/rubygem-http_parser.rb',
        'centos-opstools/rubygem-i18n',
        'centos-opstools/rubygem-idn',
        'centos-opstools/rubygem-introspection',
        'centos-opstools/rubygem-json',
        'centos-opstools/rubygem-kubeclient',
        'centos-opstools/rubygem-launchy',
        'centos-opstools/rubygem-lru_redux',
        'centos-opstools/rubygem-metaclass',
        'centos-opstools/rubygem-mime-types',
        'centos-opstools/rubygem-mime-types-data',
        'centos-opstools/rubygem-minitest',
        'centos-opstools/rubygem-mocha',
        'centos-opstools/rubygem-msgpack',
        'centos-opstools/rubygem-multi_json',
        'centos-opstools/rubygem-multi_test',
        'centos-opstools/rubygem-netrc',
        'centos-opstools/rubygem-oj',
        'centos-opstools/rubygem-parse-cron',
        'centos-opstools/rubygem-power_assert',
        'centos-opstools/rubygem-proxifier',
        'centos-opstools/rubygem-public_suffix',
        'centos-opstools/rubygem-rack',
        'centos-opstools/rubygem-recursive-open-struct',
        'centos-opstools/rubygem-resolve-hostname',
        'centos-opstools/rubygem-rest-client',
        'centos-opstools/rubygem-rr',
        'centos-opstools/rubygem-rspec',
        'centos-opstools/rubygem-rspec-core',
        'centos-opstools/rubygem-rspec-expectations',
        'centos-opstools/rubygem-rspec-its',
        'centos-opstools/rubygem-rspec-mocks',
        'centos-opstools/rubygem-rspec-support',
        'centos-opstools/rubygem-sensu-extension',
        'centos-opstools/rubygem-sensu-extensions',
        'centos-opstools/rubygem-sensu-extensions-check-dependencies',
        'centos-opstools/rubygem-sensu-extensions-debug',
        'centos-opstools/rubygem-sensu-extensions-json',
        'centos-opstools/rubygem-sensu-extensions-occurrences',
        'centos-opstools/rubygem-sensu-extensions-only-check-output',
        'centos-opstools/rubygem-sensu-extensions-ruby-hash',
        'centos-opstools/rubygem-sensu-extensions-system-profile',
        'centos-opstools/rubygem-sensu-json',
        'centos-opstools/rubygem-sensu-logger',
        'centos-opstools/rubygem-sensu-redis',
        'centos-opstools/rubygem-sensu-settings',
        'centos-opstools/rubygem-sensu-spawn',
        'centos-opstools/rubygem-sensu-transport',
        'centos-opstools/rubygem-session',
        'centos-opstools/rubygem-shoulda',
        'centos-opstools/rubygem-sigdump',
        'centos-opstools/rubygem-simplecov',
        'centos-opstools/rubygem-simplecov-html',
        'centos-opstools/rubygem-string-scrub',
        'centos-opstools/rubygem-term-ansicolor',
        'centos-opstools/rubygem-test-unit',
        'centos-opstools/rubygem-test-unit-rr',
        'centos-opstools/rubygem-thor',
        'centos-opstools/rubygem-thread_safe',
        'centos-opstools/rubygem-tins',
        'centos-opstools/rubygem-tzinfo',
        'centos-opstools/rubygem-tzinfo-data',
        'centos-opstools/rubygem-unf',
        'centos-opstools/rubygem-unf_ext',
        'centos-opstools/rubygem-uuidtools',
        'centos-opstools/rubygem-yajl-ruby',
        'centos-opstools/sensu',
        'centos-opstools/skydive',
        'rdoinfo',
        'rdo-infra/sinkhole',
        'centos-opstools/opstools-doc',
        'rdo-infra/fedora-stable-config',
        'openstack/whitebox-tempest-plugin',
        'rdo-infra/ci-config',
        'openstack/aodh-distgit',
        'openstack/aodhclient-distgit',
        'openstack/barbican-distgit',
        'openstack/barbicanclient-distgit',
        'openstack/ceilometer-distgit',
        'openstack/ceilometerclient-distgit',
        'openstack/ceilometermiddleware-distgit',
        'openstack/cinder-distgit',
        'openstack/cinderclient-distgit',
        'openstack/glance-distgit',
        'openstack/glanceclient-distgit',
        'openstack/glance_store-distgit',
        'openstack/gnocchi-distgit',
        'openstack/gnocchiclient-distgit',
        'openstack/heat-distgit',
        'openstack/heatclient-distgit',
        'openstack/heat-templates-distgit',
        'openstack/keystone-distgit',
        'openstack/keystoneauth1-distgit',
        'openstack/keystoneclient-distgit',
        'openstack/keystonemiddleware-distgit',
        'openstack/networking-bgpvpn-distgit',
        'openstack/neutron-distgit',
        'openstack/neutronclient-distgit',
        'openstack/neutron-lib-distgit',
        'openstack/neutron-fwaas-distgit',
        'openstack/neutron-lbaas-distgit',
        'openstack/neutron-lbaas-dashboard-distgit',
        'openstack/neutron-vpnaas-distgit',
        'openstack/nova-distgit',
        'openstack/novaclient-distgit',
        'openstack/openstackclient-distgit',
        'openstack/osc-lib-distgit',
        'openstack/os-brick-distgit',
        'openstack/os-client-config-distgit',
        'openstack/os-cloud-config-distgit',
        'openstack/oslo-cache-distgit',
        'openstack/oslo-config-distgit',
        'openstack/oslo-context-distgit',
        'openstack/oslo-concurrency-distgit',
        'openstack/oslo-db-distgit',
        'openstack/oslo-i18n-distgit',
        'openstack/oslo-log-distgit',
        'openstack/oslo-messaging-distgit',
        'openstack/oslo-middleware-distgit',
        'openstack/oslo-policy-distgit',
        'openstack/oslo-privsep-distgit',
        'openstack/oslo-reports-distgit',
        'openstack/oslo-rootwrap-distgit',
        'openstack/oslo-serialization-distgit',
        'openstack/oslo-service-distgit',
        'openstack/oslo-sphinx-distgit',
        'openstack/oslotest-distgit',
        'openstack/oslo-utils-distgit',
        'openstack/oslo-versionedobjects-distgit',
        'openstack/pycadf-distgit',
        'openstack/stevedore-distgit',
        'openstack/taskflow-distgit',
        'openstack/watcher-distgit',
        'openstack/zaqar-distgit',
        'openstack/zaqarclient-distgit',
        'openstack/horizon-distgit',
        'puppet/puppet-aodh-distgit',
        'puppet/puppet-apache-distgit',
        'puppet/puppet-concat-distgit',
        'puppet/puppet-ceilometer-distgit',
        'puppet/puppet-ceph-distgit',
        'puppet/puppet-cinder-distgit',
        'puppet/puppet-glance-distgit',
        'puppet/puppet-gnocchi-distgit',
        'puppet/puppet-heat-distgit',
        'puppet/puppet-keystone-distgit',
        'puppet/puppet-mongodb-distgit',
        'puppet/puppet-mysql-distgit',
        'puppet/puppet-neutron-distgit',
        'puppet/puppet-nova-distgit',
        'puppet/puppet-openstack_extras-distgit',
        'puppet/puppet-openstacklib-distgit',
        'puppet/puppet-oslo-distgit',
        'puppet/puppet-rabbitmq-distgit',
        'puppet/puppet-stdlib-distgit',
        'puppet/puppet-sysctl-distgit',
        'puppet/puppet-tempest-distgit',
        'puppet/puppet-zaqar-distgit',
        'puppet/puppet-tripleo',
        'openstack/glance',
        'openstack/heat',
        'openstack/ironic',
        'openstack/ironic-inspector',
        'openstack/ironic-python-agent',
        'openstack/mistral',
        'openstack/neutron',
        'openstack/nova',
        'openstack/dib-utils',
        'openstack/diskimage-builder',
        'openstack/instack',
        'openstack/instack-undercloud',
        'openstack/os-apply-config',
        'openstack/os-collect-config',
        'openstack/os-net-config',
        'openstack/os-refresh-config',
        'openstack/paunch',
        'openstack/tempest',
        'openstack/tripleo-common',
        'openstack/tripleo-heat-templates',
        'openstack/tripleo-image-elements',
        'openstack/tripleo-ipsec',
        'openstack/tripleo-puppet-elements',
        'openstack-infra/tripleo-ci',
    ],
    'gerritbot': [
        'openstack/whitebox-tempest-plugin',
        'testbranching',
        'testproject',
    ]
}


def print_header(text):
    print("#" * (len(text) + 4))
    print("# " + text + " #")
    print("#" * (len(text) + 4))


def project_in_replication(project):
    for pattern in replication_patterns:
        if pattern.match(project) or \
                        project in IGNORED_PROJECTS['replication']:
            return True

    # This is tricky - we have some logic to adhere to here.
    # We don't replicate project sources, only their -distgit repositories.
    # Additionally, we also don't replicate puppet repositories.
    # Try to detect this without having to whitelist explicitely each and every
    # project.

    # "<project>-distgit-distgit" wouldn't be in projects
    if ("%s-distgit" % project in projects) or \
            (project.startswith('puppet') and project.endswith('distgit')):
        return True
    return False


def project_in_zuul(project):
    if project in zuul_projects or \
            project in IGNORED_PROJECTS['zuul']:
        return True
    return False


def project_in_gerritbot(project):
    if project in gerritbot_projects or \
            project in IGNORED_PROJECTS['gerritbot']:
        return True
    return False

###
# Retrieve Gerrit project list
###
# Gerrit's response is pretty-printed JSON but the first line is garbage, get
# rid of it
try:
    projects = requests.get(PROJECT_LIST)
    projects = json.loads(projects.text.replace(")]}'\n", ""))
except ValueError as e:
    print_header("Error when retrieving project list from Gerrit")
    print("HTTP: %s" % projects.status_code)
    print("Content: %s" % projects.text)
    raise e

###
# Retrieve Gerrit replication.config
###
# replication.config is really just a ini-like config file with leading spaces
# for the parameters, load it properly by stripping the whitespace
with open('gerrit/replication.config') as file:
    config = file.readlines()
replication = configparser.ConfigParser()
replication.readfp(StringIO(''.join([l.lstrip() for l in config])))

# What we're really interested from the replication.config file is the projects
# field which is a pattern we want to be matching against
replication_patterns = []
for section in replication.sections():
    try:
        pattern = re.compile(replication.get(section, 'projects'))
        replication_patterns.append(pattern)
    except configparser.NoOptionError:
        pass

###
# Retrieve list of projects in Gerritbot
###
gerritbot_projects = []
with open('gerritbot/channels.yaml') as f:
    config = yaml.load(f.read())
    irc_rdo = config['rdo']['projects']
    irc_opstools = config['centos-opstools']['projects']
    for project in irc_rdo + irc_opstools:
        gerritbot_projects.append(project)

###
# Retrieve list of projects in Zuul layout
###
zuul_files = glob.glob('zuul/*.yaml')
zuul_projects = []
for file in zuul_files:
    with open(file, 'r') as f:
        config = yaml.load(f.read())
    for project in config['projects']:
        zuul_projects.append(project['name'])


error = False
errors = collections.defaultdict(lambda: [])
for project in projects:
    # Check if project is replicated
    if not project_in_replication(project):
            error = True
            errors['replication'].append(project)

    # Check if project is in gerritbot
    if not project_in_gerritbot(project):
        error = True
        errors['gerritbot'].append(project)

    # Check if project is in zuul layout
    if not project_in_zuul(project):
        error = True
        errors['zuul'].append(project)

if errors['replication']:
    print_header("Projects not in Gerrit Replication")
    for e in sorted(errors['replication']):
        print(e)

if errors['zuul']:
    print_header("Projects not in Zuul Layout")
    for e in sorted(errors['zuul']):
        print(e)

if errors['gerritbot']:
    print_header("Projects not in Gerritbot")
    for e in sorted(errors['gerritbot']):
        print(e)

sys.exit(error)
