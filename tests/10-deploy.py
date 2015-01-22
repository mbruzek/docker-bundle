#!/usr/bin/env python3

# This is an integration test for the flannel-docker charm.

import amulet
import unittest
import os
import yaml

seconds = 1200


class BundleIntegrationTests(unittest.TestCase):
    """ Integration tests for deploying a bundle. """
    bundle = None

    @classmethod
    def setUpClass(self):
        """
        The setup method runs once after the class is created.
        """
        if self.bundle:
            self.bundle_path = os.path.abspath(self.bundle)
        else:
            self.bundle_path = os.path.join(os.path.dirname(__file__),
                                            '..',
                                            'bundles.yaml')

        self.deployment = amulet.Deployment(series='trusty')

        with open(self.bundle_path, 'r') as bundle_file:
            contents = yaml.safe_load(bundle_file)
            self.deployment.load(contents)

        try:
            self.deployment.setup(timeout=seconds)
            self.deployment.sentry.wait()
        except amulet.helpers.TimeoutError:
            msg = "The environment was not set up in %d seconds." % seconds
            amulet.raise_status(amulet.FAIL, msg)
        except:
            raise

        self.docker_unit = self.deployment.sentry.unit['docker/0']
        self.etcd_unit = self.deployment.sentry.unit['etcd/0']

    def test_docker_1(self):
        """ Check if the docker binary is installed. """
        stat = self.docker_unit.file_stat('/usr/bin/docker')
        if not stat:
            amulet.raise_status(amulet.FAIL, msg='Docker binary missing!')

    def test_docker_info(self):
        """ Get the Docker information """
        output, code = self.docker_unit.run('docker info')
        print(output)
        if code != 0:
            message = 'The docker info command failed with %d' % code
            amulet.raise_status(amulet.FAIL, msg=message)

    def test_docker_busybox(self):
        """ Pull down the busybox container and run."""
        command = 'docker pull busybox'
        output, code = self.docker_unit.run(command)
        print(output)
        if code != 0:
            if output.find('latest not found') != -1:
                message = 'Could not pull the busybox docker container!'
                amulet.raise_status(amulet.FAIL, msg=message)
        command = 'docker run busybox echo hello world'
        output, code = self.docker_unit.run(command)
        print(output)
        if code != -0:
            message = 'Could not run echo on the busybox container.'
            amulet.raise_status(amulet.FAIL, msg=message)
        command = 'docker rmi -f busybox'
        output, code = self.docker_unit.run(command)
        print(output)
        if code != -0:
            message = 'Could not delete the busybox container.'
            amulet.raise_status(amulet.FAIL, msg=message)

    def test_latest_config_option(self):
        """ Set config option to latest and verify docker is installed """
        self.deployment.configure('docker', {'latest': True})
        self.deployment.sentry.wait()
        command = 'dpkg -l lxc-docker'
        output, code = self.docker_unit.run(command)
        print(output)
        if output.find('ii') == -1:
            message = 'Could not upgrade docker to latest!'
            amulet.raise_status(amulet.FAIL, msg=message)
        command = 'dpkg -l docker.io'
        output, code = self.docker_unit.run(command)
        print(output)
        if output.find('ii') != -1:
            message = "Leftover docker.io package found"
            amulet.raise_status(amulet.Fail, msg=message)

    def test_flannel_binary(self):
        """ Test to see if flannel is installed correctly. """
        command = 'flannel --version'
        # Run the command to see if flannel is installed on the docker unit.
        output, code = self.docker_unit.run(command)
        print(command, output)
        if code != 0:
            message = 'The flannel binary is not installed.'
            amulet.raise_status(amulet.FAIL, msg=message)

    def test_flannel_running(self):
        """ Test to see if flannel is running correctly. """
        command = 'sudo service flannel status'
        # Run the command to see if flannel is running on the docker unit.
        output, code = self.docker_unit.run(command)
        print(command, output)
        if code != 0:
            message = 'The flannel process is not in correct status.'
            amulet.raise_status(amulet.FAIL, msg=message)

    def test_flannel_config(self):
        """ Test the flannel configuration. """
        flannel_config_file = '/etc/init/flannel.conf'
        # Get the flannel configuration file on the docker unit.
        flannel_config = self.docker_unit.file_contents(flannel_config_file)
        etcd_public_address = self.etcd_unit.info['public-address']
        print('etcd public address:', etcd_public_address)
        # Must get the etcd relation to get the relation information.
        etcd_relation = self.etcd_unit.relation('client', 'flannel-docker:db')
        etcd_private_address = etcd_relation['private-address']
        print('etcd private address:', etcd_private_address)
        etcd_port = etcd_relation['port']
        print('etcd port:', etcd_port)
        # Search the configuration for the etcd private address.
        address_index = flannel_config.find(etcd_private_address)
        # Search the configuration for the etcd port.
        port_index = flannel_config.find(etcd_port)
        found_address = address_index != -1
        found_port = port_index != -1
        if found_address and found_port:
            print('The flannel configuration had correct etcd information.')
        else:
            print(flannel_config)
            message = 'Flannel did not have the correct etcd information.'
            amulet.raise_status(amulet.FAIL, msg=message)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--bundle', default=None)
    pargs = parser.parse_args()
    BundleIntegrationTests.bundle = pargs.bundle
    unittest.main()
