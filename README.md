# docker-bundle

The Docker Core bundle deploys 2 docker hosts, etcd, and flannel overlay
networking to 'bootstrap' a docker container cluster farm. This enables
a rapid buildout to deploy containers for production usage.


## Usage

Assuming you have the bundle repository cloned locally:

    juju quickstart docker-core/bundles.yaml

This will bootstrap your active environment (if one is not already active) and
deploy the services.


## Scaling the Services

To scale the container farm, simply add more units to the docker service

    juju add-unit docker


## Known Limitations

This bundle will **not** work on the local provider or when using --to lxc
scenarios. AppArmor has a very stringent default policy that breaks the
functionality of docker/flannel being embedded in LXC.

ETCD is currently deployed as a single node, and has not been tested
by adding additional ETCD units. This can provide a single point of failure if
the ETCD unit were to 'go away'.

The bundle makes assumptions about each service being on it's own machine. Its
a common practice to deploy the ETCD unit to the state-server if you have the
capacity to co-locate on machine 0 of your environment

    juju deploy cs:~hazmat/trusty/etcd --to 0



## More Information

- [Docker Charm on GitHub](https://github.com/chuckbutler/docker-charm)
- [Docker Charm Docs](http://chuckbutler.github.io/docker-charm/)
- [Docker Charm Bugtracker](https://github.com/chuckbutler/docker-charm/issues)
- [Flannel-Docker Charm on Github](https://github.com/chuckbutler/flannel-docker-charm)
- [Flannel Docker Docs](http://chuckbutler.github.io/flannel-docker-charm/)
- [Flannel Docker Bugtracker](https://github.com/chuckbutler/flannel-docker-charm/issues)
