# Copyright 2018: Red Hat Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from urllib.request import urlopen

from rally.common import logging
from rally import exceptions
from rally.task import types
from rally.task import utils as rally_utils
from rally.task import validation

from rally_openstack.common import consts
from rally_openstack.common.wrappers import network as network_wrapper
from rally_openstack.task import scenario
from rally_openstack.task.scenarios.octavia import utils as octavia_utils
from rally_openstack.task.scenarios.vm import utils as vm_utils


"""Scenarios for Octavia Loadbalancer."""


LOG = logging.getLogger(__name__)


@validation.add("required_services", services=[consts.Service.OCTAVIA])
@validation.add("required_platform", platform="openstack", users=True)
@validation.add("required_contexts", contexts=["network"])
@scenario.configure(context={"cleanup@openstack": ["octavia"]},
                    name="Octavia.create_and_list_loadbalancers",
                    platform="openstack")
class CreateAndListLoadbalancers(octavia_utils.OctaviaBase):

    def run(self, description=None, admin_state=True,
            listeners=None, flavor_id=None, provider=None,
            vip_qos_policy_id=None):
        """Create a loadbalancer per each subnet and then list loadbalancers.

        :param description: Human-readable description of the loadbalancer
        :param admin_state: The administrative state of the loadbalancer,
            which is up(true) or down(false)
        :param listeners: The associated listener id, if any
        :param flavor_id: The ID of the flavor
        :param provider: Provider name for the loadbalancer
        :param vip_qos_policy_id: The ID of the QoS policy
        """
        subnets = []
        loadbalancers = []
        networks = self.context.get("tenant", {}).get("networks", [])
        project_id = self.context["tenant"]["id"]
        for network in networks:
            subnets.extend(network.get("subnets", []))
        for subnet_id in subnets:
            lb = self.octavia.load_balancer_create(
                subnet_id=subnet_id,
                description=description,
                admin_state=admin_state,
                project_id=project_id,
                listeners=listeners,
                flavor_id=flavor_id,
                provider=provider,
                vip_qos_policy_id=vip_qos_policy_id)
            loadbalancers.append(lb)

        for loadbalancer in loadbalancers:
            self.octavia.wait_for_loadbalancer_prov_status(loadbalancer)
        self.octavia.load_balancer_list()


@validation.add("required_services", services=[consts.Service.OCTAVIA])
@validation.add("required_platform", platform="openstack", users=True)
@validation.add("required_contexts", contexts=["network"])
@scenario.configure(context={"cleanup@openstack": ["octavia"]},
                    name="Octavia.create_and_delete_loadbalancers",
                    platform="openstack")
class CreateAndDeleteLoadbalancers(octavia_utils.OctaviaBase):

    def run(self, description=None, admin_state=True,
            listeners=None, flavor_id=None, provider=None,
            vip_qos_policy_id=None):
        """Create a loadbalancer per each subnet and then delete loadbalancer

        :param description: Human-readable description of the loadbalancer
        :param admin_state: The administrative state of the loadbalancer,
            which is up(true) or down(false)
        :param listeners: The associated listener id, if any
        :param flavor_id: The ID of the flavor
        :param provider: Provider name for the loadbalancer
        :param vip_qos_policy_id: The ID of the QoS policy
        """
        subnets = []
        loadbalancers = []
        networks = self.context.get("tenant", {}).get("networks", [])
        project_id = self.context["tenant"]["id"]
        for network in networks:
            subnets.extend(network.get("subnets", []))
        for subnet_id in subnets:
            lb = self.octavia.load_balancer_create(
                subnet_id=subnet_id,
                description=description,
                admin_state=admin_state,
                project_id=project_id,
                listeners=listeners,
                flavor_id=flavor_id,
                provider=provider,
                vip_qos_policy_id=vip_qos_policy_id)
            loadbalancers.append(lb)

        for loadbalancer in loadbalancers:
            self.octavia.wait_for_loadbalancer_prov_status(loadbalancer)
            self.octavia.load_balancer_delete(
                loadbalancer["id"])


@validation.add("required_services", services=[consts.Service.OCTAVIA])
@validation.add("required_platform", platform="openstack", users=True)
@validation.add("required_contexts", contexts=["network"])
@scenario.configure(context={"cleanup@openstack": ["octavia"]},
                    name="Octavia.create_and_update_loadbalancers",
                    platform="openstack")
class CreateAndUpdateLoadBalancers(octavia_utils.OctaviaBase):

    def run(self, description=None, admin_state=True,
            listeners=None, flavor_id=None, provider=None,
            vip_qos_policy_id=None):
        """Create a loadbalancer per each subnet and then update

        :param description: Human-readable description of the loadbalancer
        :param admin_state: The administrative state of the loadbalancer,
            which is up(true) or down(false)
        :param listeners: The associated listener id, if any
        :param flavor_id: The ID of the flavor
        :param provider: Provider name for the loadbalancer
        :param vip_qos_policy_id: The ID of the QoS policy
        """
        subnets = []
        loadbalancers = []
        networks = self.context.get("tenant", {}).get("networks", [])
        project_id = self.context["tenant"]["id"]
        for network in networks:
            subnets.extend(network.get("subnets", []))
        for subnet_id in subnets:
            lb = self.octavia.load_balancer_create(
                subnet_id=subnet_id,
                description=description,
                admin_state=admin_state,
                project_id=project_id,
                listeners=listeners,
                flavor_id=flavor_id,
                provider=provider,
                vip_qos_policy_id=vip_qos_policy_id)
            loadbalancers.append(lb)

            update_loadbalancer = {
                "name": self.generate_random_name()
            }

        for loadbalancer in loadbalancers:
            self.octavia.wait_for_loadbalancer_prov_status(loadbalancer)
            self.octavia.load_balancer_set(
                lb_id=loadbalancer["id"],
                lb_update_args=update_loadbalancer)


@validation.add("required_services", services=[consts.Service.OCTAVIA])
@validation.add("required_platform", platform="openstack", users=True)
@validation.add("required_contexts", contexts=["network"])
@scenario.configure(context={"cleanup@openstack": ["octavia"]},
                    name="Octavia.create_and_stats_loadbalancers",
                    platform="openstack")
class CreateAndShowStatsLoadBalancers(octavia_utils.OctaviaBase):

    def run(self, description=None, admin_state=True,
            listeners=None, flavor_id=None, provider=None,
            vip_qos_policy_id=None):
        """Create a loadbalancer per each subnet and stats

        :param description: Human-readable description of the loadbalancer
        :param admin_state: The administrative state of the loadbalancer,
            which is up(true) or down(false)
        :param listeners: The associated listener id, if any
        :param flavor_id: The ID of the flavor
        :param provider: Provider name for the loadbalancer
        :param vip_qos_policy_id: The ID of the QoS policy
        """
        subnets = []
        loadbalancers = []
        networks = self.context.get("tenant", {}).get("networks", [])
        project_id = self.context["tenant"]["id"]
        for network in networks:
            subnets.extend(network.get("subnets", []))
        for subnet_id in subnets:
            lb = self.octavia.load_balancer_create(
                subnet_id=subnet_id,
                description=description,
                admin_state=admin_state,
                project_id=project_id,
                listeners=listeners,
                flavor_id=flavor_id,
                provider=provider,
                vip_qos_policy_id=vip_qos_policy_id)
            loadbalancers.append(lb)

        for loadbalancer in loadbalancers:
            self.octavia.wait_for_loadbalancer_prov_status(loadbalancer)
            self.octavia.load_balancer_stats_show(
                loadbalancer["id"])


@validation.add("required_services", services=[consts.Service.OCTAVIA])
@validation.add("required_platform", platform="openstack", users=True)
@validation.add("required_contexts", contexts=["network"])
@scenario.configure(context={"cleanup@openstack": ["octavia"]},
                    name="Octavia.create_and_show_loadbalancers",
                    platform="openstack")
class CreateAndShowLoadBalancers(octavia_utils.OctaviaBase):

    def run(self, description=None, admin_state=True,
            listeners=None, flavor_id=None, provider=None,
            vip_qos_policy_id=None):
        """Create a loadbalancer per each subnet and then compare

        :param description: Human-readable description of the loadbalancer
        :param admin_state: The administrative state of the loadbalancer,
            which is up(true) or down(false)
        :param listeners: The associated listener id, if any
        :param flavor_id: The ID of the flavor
        :param provider: Provider name for the loadbalancer
        :param vip_qos_policy_id: The ID of the QoS policy
        """
        subnets = []
        loadbalancers = []
        networks = self.context.get("tenant", {}).get("networks", [])
        project_id = self.context["tenant"]["id"]
        for network in networks:
            subnets.extend(network.get("subnets", []))
        for subnet_id in subnets:
            lb = self.octavia.load_balancer_create(
                subnet_id=subnet_id,
                description=description,
                admin_state=admin_state,
                project_id=project_id,
                listeners=listeners,
                flavor_id=flavor_id,
                provider=provider,
                vip_qos_policy_id=vip_qos_policy_id)
            loadbalancers.append(lb)

        for loadbalancer in loadbalancers:
            self.octavia.wait_for_loadbalancer_prov_status(loadbalancer)
            self.octavia.load_balancer_show(
                loadbalancer["id"])


@types.convert(image={"type": "glance_image"},
               flavor={"type": "nova_flavor"},
               floating_net={"type": "neutron_network"})
@validation.add("image_valid_on_flavor", flavor_param="flavor",
                image_param="image")
@validation.add("required_services", services=[consts.Service.OCTAVIA,
                                               consts.Service.NOVA])
@validation.add("required_platform", platform="openstack", users=True)
@validation.add("required_contexts", contexts=["network"])
@scenario.configure(context={"cleanup@openstack": ["octavia", "nova",
                                                   "neutron"],
                             "keypair@openstack": {},
                             "allow_ssh@openstack": None},
                    name="Octavia.create_and_balance_http_vms",
                    platform="openstack")
class CreateAndBalanceHttpVms(octavia_utils.OctaviaBase, vm_utils.VMScenario):

    def run(self, image, flavor, username, password=None,
            floating_net=None, port=22, use_floating_ip=True,
            description=None, admin_state=True, listeners=None,
            flavor_id=None, provider=None, vip_qos_policy_id=None, **kwargs):
        """Create a loadbalancer in front of two apache servers.

        :param image: The image to boot from
        :param flavor: Flavor used to boot instance
        :param username: ssh username on server
        :param password: Password on SSH authentication
        :param floating_net: external network name, for floating ip
        :param port: ssh port for SSH connection
        :param use_floating_ip: bool, floating or fixed IP for SSH connection
        :param description: Human-readable description of the loadbalancer
        :param admin_state: The administrative state of the loadbalancer,
            which is up(true) or down(false)
        :param listeners: The associated listener id, if any
        :param flavor_id: The ID of the flavor
        :param provider: Provider name for the loadbalancer
        :param vip_qos_policy_id: The ID of the QoS policy
        :param kwargs: Optional additional arguments for instance creation

        - Create a loadbalancer
        - Create a listener for protocal HTTP on port 80
        - Create a pool using ROUND_ROBIN and protocal HTTP
        - Create two VMs, installing apache2 from cloud-init
        - Wait for loadbalancer and server resources to become ACTIVE
        - Create a loadbalancer member for each VM
        - Assign a floating IP to the loadbalancer port
        - Verify that a connection can be established to port 80 at the FIP
        """
        project_id = self.context["tenant"]["id"]
        network = self.context["tenant"]["networks"][0]
        subnet = network["subnets"][0]

        security_group_create_args = {"name": self.generate_random_name()}
        security_group = self.clients("neutron").create_security_group(
            {"security_group": security_group_create_args})
        sg_id = security_group["security_group"]["id"]
        security_group_rule_args = {
            "security_group_id": sg_id,
            "direction": "ingress",
            "port_range_max": 80,
            "port_range_min": 80,
            "protocol": "tcp",
            "remote_ip_prefix": "0.0.0.0/0",
        }
        self.clients("neutron").create_security_group_rule(
            {"security_group_rule": security_group_rule_args})

        fnet = {"id": floating_net}
        lp_fip = network_wrapper.wrap(self.clients, self).create_floating_ip(
            ext_network=fnet, tenant_id=project_id)

        lb = self.octavia.load_balancer_create(
            subnet_id=subnet,
            description=description,
            admin_state=admin_state,
            project_id=project_id,
            listeners=listeners,
            flavor_id=flavor_id,
            provider=provider,
            vip_qos_policy_id=vip_qos_policy_id
        )

        LOG.info("Waiting for Octavia loadbalancer to become ready.")
        self.octavia.wait_for_loadbalancer_prov_status(lb)
        lb_id = lb["id"]

        largs = {
            "protocol": "HTTP",
            "protocol_port": 80,
            "loadbalancer_id": lb_id,
        }
        listener = self.octavia.listener_create(json={"listener": largs})
        l1 = listener["listener"]

        self.octavia.wait_for_listener_prov_status(l1)

        pool = self.octavia.pool_create(
            lb_id=lb_id,
            protocol="HTTP",
            lb_algorithm="ROUND_ROBIN",
            listener_id=l1["id"],
            project_id=project_id,
        )

        # Assign the FIP to the loadbalancer
        fip_update_dict = {"port_id": lb["vip_port_id"]}
        self.clients("neutron").update_floatingip(
            lp_fip["id"], {"floatingip": fip_update_dict})

        # Place a couple http servers behind the loadbalancer
        for s in range(2):
            server, fip = self._boot_server_with_fip(
                image, flavor, use_floating_ip=use_floating_ip,
                floating_net=floating_net,
                key_name=self.context["user"]["keypair"]["name"],
                userdata="#cloud-config\npackages:\n - apache2",
                **kwargs)

            server_address = server.addresses[network["name"]][0]["addr"]

            margs = {
                "address": server_address,
                "protocol_port": 80,
            }
            self.octavia.member_create(
                pool["id"], json={"member": margs})

            # Allow http access to the server
            self._add_server_secgroups(server, sg_id)

            LOG.info("Added server with IP %s as a member to pool: %s"
                     % (server_address, pool["id"]))

            # It takes some time for the server to become ready.
            # Be sure the server network is available before proceeding.
            script = "cloud-init status -w || exit 1"

            command = {
                "script_inline": script,
                "interpreter": "/bin/bash"
            }

            LOG.info("Waiting for server instance to become ready.")
            rally_utils.wait_for_status(
                server,
                ready_statuses=["ACTIVE"],
                update_resource=rally_utils.get_from_manager(),
            )

            code, out, err = self._run_command(
                fip["ip"], port, username, password, command=command)
            if code:
                raise exceptions.ScriptError(
                    "Error running command %(command)s. "
                    "Error %(code)s: %(error)s" % {
                        "command": command, "code": code, "error": err})

        # Verifiy the http servers can be reached on the loadbalancer FIP.
        response = urlopen("http://%s/" % lp_fip["ip"])
        r_code = response.getcode()
        if r_code != 200:
            raise exceptions.RallyException(
                "Received unexpected error when connecting to %s: %d"
                % (lp_fip["ip"], r_code))
        LOG.info("Successfully connected to Octavia loadbalancer at http://%s/"
                 % lp_fip["ip"])
