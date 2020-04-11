# Copyright 2020 Canonical Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from unittest import mock

import ddt

from rally import exceptions

from rally_openstack.task.scenarios.octavia import loadbalancers
from tests.unit import test


OCTAVIA_LB = "rally_openstack.task.scenarios.octavia.loadbalancers."


@ddt.ddt
class LoadbalancersTestCase(test.ScenarioTestCase):

    def setUp(self):
        super(LoadbalancersTestCase, self).setUp()
        self.context.update({
            "user": {"keypair": {"name": "foo_keypair_name"},
                     "credential": mock.MagicMock()},
            "tenant": {"id": "foo_tenant_id",
                       "networks": [{
                           "name": "foo_net",
                           "subnets": ["foo_subnet0"]
                       }]}
        })

        cinder_patcher = mock.patch(
            "rally_openstack.common.services.storage.block.BlockStorage")
        self.cinder = cinder_patcher.start().return_value
        self.cinder.create_volume.return_value = mock.Mock(id="foo_volume")
        self.addCleanup(cinder_patcher.stop)

    def create_env(self, scenario):
        self.ip = {"id": "foo_id", "ip": "foo_ip", "is_floating": True}

        scenario.generate_random_name = mock.Mock(
            return_value="random_name")

        scenario.octavia.load_balancer_create = mock.Mock(
            return_value={"id": "foo_lb_id", "vip_port_id": 1234}
        )
        scenario.octavia.wait_for_loadbalancer_prov_status = mock.Mock(
            return_value=True
        )
        scenario.octavia.listener_create = mock.Mock(
            return_value={"listener": {"id": "listener_id"}}
        )

        scenario.octavia.wait_for_listener_prov_status = mock.Mock()

        scenario.octavia.pool_create = mock.Mock(
            return_value={"id": "pool_id"}
        )

        scenario.server = mock.Mock(
            networks={"foo_net": {"subnets": "foo_subnet"}},
            addresses={"foo_net": [{"addr": "foo_ip"}]},
            tenant_id="foo_tenant"
        )

        scenario._boot_server_with_fip = mock.Mock(
            return_value=(scenario.server, self.ip))

        scenario.octavia.member_create = mock.Mock()

        scenario._add_server_secgroups = mock.Mock()

        # wait_for_status and get_from_manager are mocked in the base class as
        # self.mock_wait_for_status and self.mock_get_from_manager

        scenario._run_command = mock.MagicMock(
            return_value=(0, "{\"foo\": 42}", "foo_err"))

        return scenario

    @ddt.data({
        "image": "foo_image", "flavor": "foo_flavor", "username": "foo_user",
        "password": "foo_password", "floating_net": "foo_floating_net",
        "port": "foo_port", "use_floating_ip": "foo_use_floating_ip",
        "description": "foo_description", "admin_state": "foo_admin_state",
        "listeners": "foo_listeners", "flavor_id": "foo_flavor_id",
        "provider": "foo_provider",
        "vip_qos_policy_id": "foo_vip_qos_policy_id",
    })
    @mock.patch(OCTAVIA_LB + "urlopen")
    @mock.patch(OCTAVIA_LB + "network_wrapper.wrap")
    def test_create_and_balance_http_vms(self, params, mock_wrap,
                                         mock_urlopen):
        scenario = self.create_env(
            loadbalancers.CreateAndBalanceHttpVms(self.context))

        # Mock a successful response from urlopen.
        mock_response = mock.MagicMock()
        mock_response.getcode.side_effect = [200]
        mock_urlopen.return_value = mock_response

        # self.clients is mocked in the base class
        # Set a return value for self.clients("neutron").create_security_group
        sec_grp = {"security_group": {"id": "sec_grp_id"}}
        self.clients(
            "neutron").create_security_group.return_value = sec_grp

        netwrap = mock_wrap.return_value
        fip = {"id": "foo_id", "ip": "foo_ip"}
        netwrap.create_floating_ip.return_value = fip

        scenario._run_command = mock.MagicMock(
            return_value=(0, "{\"foo\": 42}", "foo_err"))

        scenario.run(**params)

        # Check load_balancer_createte_security_group_rule is called with
        #  expected args.
        expected_security_group_rule_args = {
            "security_group_id": "sec_grp_id",
            "direction": "ingress",
            "port_range_max": 80,
            "port_range_min": 80,
            "protocol": "tcp",
            "remote_ip_prefix": "0.0.0.0/0",
        }
        self.clients(
            "neutron").create_security_group_rule.assert_called_once_with(
                {"security_group_rule": expected_security_group_rule_args})

        # create_floating_ip

        # Check load_balancer_create is called with expected args.
        expected_lb_create_args = {
            "subnet_id": "foo_subnet0",
            "description": "foo_description",
            "admin_state": "foo_admin_state",
            "project_id": "foo_tenant_id",
            "listeners": "foo_listeners",
            "flavor_id": "foo_flavor_id",
            "provider": "foo_provider",
            "vip_qos_policy_id": "foo_vip_qos_policy_id",
        }
        scenario.octavia.load_balancer_create.assert_called_once_with(
            **expected_lb_create_args)

        # Check listener_create is called with expected args.
        expected_listener_create_args = {
            "json": {
                "listener": {
                    "protocol": "HTTP",
                    "protocol_port": 80,
                    "loadbalancer_id": "foo_lb_id",
                }
            }
        }
        scenario.octavia.listener_create.assert_called_once_with(
            **expected_listener_create_args)

        # Check wait_for_listener_prov_status is called with expected args.
        (scenario.octavia.wait_for_loadbalancer_prov_status.
            assert_called_once_with({"id": "foo_lb_id", "vip_port_id": 1234}))

        # Check pool_create is called with expected args.
        expected_pool_create_args = {
            "lb_id": "foo_lb_id",
            "protocol": "HTTP",
            "lb_algorithm": "ROUND_ROBIN",
            "listener_id": "listener_id",
            "project_id": "foo_tenant_id",
        }
        scenario.octavia.pool_create.assert_called_once_with(
            **expected_pool_create_args)

        # Check update_floatingip is called with expected args.
        self.clients(
            "neutron").update_floatingip.assert_called_once_with(
                "foo_id", {"floatingip": {"port_id": 1234}})

        # Checks for two servers added as members to the load balancer group.
        # Check _boot_server_with_fip is called with expected args.
        expected_boot_server_args = [
            mock.call("foo_image", "foo_flavor",
                      use_floating_ip="foo_use_floating_ip",
                      floating_net="foo_floating_net",
                      key_name="foo_keypair_name",
                      userdata="#cloud-config\npackages:\n - apache2"),
            mock.call("foo_image", "foo_flavor",
                      use_floating_ip="foo_use_floating_ip",
                      floating_net="foo_floating_net",
                      key_name="foo_keypair_name",
                      userdata="#cloud-config\npackages:\n - apache2"),
        ]
        self.assertEqual(
            scenario._boot_server_with_fip.call_args_list,
            expected_boot_server_args)

        # Check member_create is called with expected args.
        expected_member_args = {
            "member": {"address": "foo_ip", "protocol_port": 80}
        }

        expected_member_args = {
            "member": {"address": "foo_ip", "protocol_port": 80}
        }
        expected_pool_create_args = [
            mock.call("pool_id", json=expected_member_args),
            mock.call("pool_id", json=expected_member_args),
        ]
        self.assertEqual(scenario.octavia.member_create.call_args_list,
                         expected_pool_create_args)

        # Check _add_server_secgroups is called with expected args.
        expected_member_args = {
            "member": {"address": "foo_ip", "protocol_port": 80}
        }
        expected_add_server_secgroups_args = [
            mock.call(scenario.server, "sec_grp_id"),
            mock.call(scenario.server, "sec_grp_id"),
        ]
        self.assertEqual(scenario._add_server_secgroups.call_args_list,
                         expected_add_server_secgroups_args)

        # Check that _run_command is called for both servers with the script
        # to wait for cloud-init to complete.
        expected_command = {
            "script_inline": "cloud-init status -w || exit 1",
            "interpreter": "/bin/bash"
        }
        expected_run_command_call_args = [
            mock.call("foo_ip", "foo_port", "foo_user", "foo_password",
                      command=expected_command),
            mock.call("foo_ip", "foo_port", "foo_user", "foo_password",
                      command=expected_command)]
        self.assertEqual(scenario._run_command.call_args_list,
                         expected_run_command_call_args)

        # Check urlopen is called with expected args.
        mock_urlopen.assert_called_once_with("http://foo_ip/")

        # Check response.getcode was called.
        mock_response.getcode.assert_called_once_with()

    @ddt.data(
        {"image": "some_image",
         "flavor": "m1.small", "username": "test_user"}
    )
    @mock.patch(OCTAVIA_LB + "urlopen")
    @mock.patch(OCTAVIA_LB + "network_wrapper.wrap")
    def test_create_and_balance_http_vms_raises_ScriptError(
            self, params, mock_wrap, mock_urlopen):
        scenario = self.create_env(
            loadbalancers.CreateAndBalanceHttpVms(self.context))

        mock_response = mock.MagicMock()
        mock_response.getcode.side_effect = [200]
        mock_urlopen.return_value = mock_response

        sec_grp = {"security_group": {"id": "sec_grp_id"}}
        self.clients(
            "neutron").create_security_group.return_value = sec_grp

        netwrap = mock_wrap.return_value
        fip = {"id": "foo_id", "ip": "foo_ip"}
        netwrap.create_floating_ip.return_value = fip

        scenario._run_command.return_value = (-1, "out", "err")
        self.assertRaises(exceptions.ScriptError,
                          scenario.run,
                          **params,
                          )

    @ddt.data(
        {"image": "some_image",
         "flavor": "m1.small", "username": "test_user"}
    )
    @mock.patch(OCTAVIA_LB + "urlopen")
    @mock.patch(OCTAVIA_LB + "network_wrapper.wrap")
    def test_create_and_balance_http_vms_raises_RallyException(
            self, params, mock_wrap, mock_urlopen):
        scenario = self.create_env(
            loadbalancers.CreateAndBalanceHttpVms(self.context))

        mock_response = mock.MagicMock()
        mock_response.getcode.side_effect = [400]
        mock_urlopen.return_value = mock_response

        sec_grp = {"security_group": {"id": "sec_grp_id"}}
        self.clients(
            "neutron").create_security_group.return_value = sec_grp

        netwrap = mock_wrap.return_value
        fip = {"id": "foo_id", "ip": "foo_ip"}
        netwrap.create_floating_ip.return_value = fip
        scenario._run_command = mock.MagicMock(
            return_value=(0, "{\"foo\": 42}", "foo_err"))
        self.assertRaises(exceptions.RallyException,
                          scenario.run,
                          **params,
                          )
