# docker-bundle

The Docker Core bundle uses juju to deploy 2 docker hosts (ie
"units"), etcd, and flannel overlay networking to 'bootstrap' a docker
container cluster farm.


## Current and Most Complete Information

- [Docker Charm on GitHub](https://github.com/chuckbutler/docker-charm)
- [Docker Charm Docs](http://chuckbutler.github.io/docker-charm/)
- [Docker Charm Bugtracker](https://github.com/chuckbutler/docker-charm/issues)
- [Flannel-Docker Charm on Github](https://github.com/chuckbutler/flannel-docker-charm)
- [Flannel Docker Docs](http://chuckbutler.github.io/flannel-docker-charm/)
- [Flannel Docker Bugtracker](https://github.com/chuckbutler/flannel-docker-charm/issues)


## TL;DR Usage

For the simplest deployment scenario, you will need `juju` and `juju
quickstart` and some credentials for a supported cloud.  On ubuntu:

    "sudo apt-get install juju-core juju-quickstart"

* If not on ubuntu, you may want to use the
[jujubox](https://github.com/whitmo/jujubox) Docker image. *

Clone the bundle repository cloned locally and run this command to set
up your cloud credentials and run the bundle:

    juju quickstart docker-core/bundles.yaml

This will bootstrap your active environment (if one is not already
active) and deploy the services.


## Scaling the Services

To scale the container farm, simply add more units to the docker
service:

    juju add-unit docker


## Using the your new docker "cluster"

To interact with your dockers, use `juju ssh` to get console on the
unit:

    juju ssh docker/0 -t sudo tmux


Use `juju run` to run remotely commands as root:

    juju run --service "docker ps"


## Known Limitations

This bundle will **not** work on the local provider or when using --to
lxc scenarios. AppArmor has a very stringent default policy that
breaks the functionality of docker/flannel being embedded in LXC.

ETCD is currently deployed as a single node, and has not been tested
by adding additional ETCD units. This can provide a single point of
failure if the ETCD unit were to 'go away'.

The bundle makes assumptions about each service being on it's own
machine. Its a common practice to deploy the ETCD unit to the
state-server if you have the capacity to co-locate on machine 0 of
your environment

    juju deploy cs:~hazmat/trusty/etcd --to 0
