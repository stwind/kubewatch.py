# kubewatch.py

A simple script to watch kubernetes resources, useful for debuging or controller development.

It works by utilizing `etcdctl watch`  for events and querying the kubernetes API for resource metadata.

Tested with

* Kubernetes v1.18.3
* Docker v19.03.11

* Ubuntu focal

## Usage

Create a service account with readonly permission on all resources.

```sh
$ kubectl apply -f - <<'EOF'
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: resource-reader
  namespace: default
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: resource-reader
rules:
  - apiGroups: ['*']
    resources: ['*']
    verbs: ['get','list']
  - nonResourceURLs: ['*']
    verbs: ['get','list']
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
 name: resource-reader
subjects:
 - kind: ServiceAccount
   name: resource-reader
   namespace: default
roleRef:
 kind: ClusterRole
 name: resource-reader
 apiGroup: rbac.authorization.k8s.io
EOF
```

And the command help

```sh
$ ./kubewatch.py -h
usage: kubewatch.py [-h] [--etcd-pod ETCD_POD] [--cluster CLUSTER] [--serviceaccount SERVICEACCOUNT] [--res-incl RES_INCL] [--res-excl RES_EXCL] [--ns-incl NS_INCL] [--ns-excl NS_EXCL] [--trunc TRUNC]

Watch kubernetes resources

optional arguments:
  -h, --help            show this help message and exit
  --etcd-pod ETCD_POD   pod of etcd
  --cluster CLUSTER     cluster to watch
  --serviceaccount SERVICEACCOUNT
                        Service Account
  --res-incl RES_INCL   comma delimited, show only resources
  --res-excl RES_EXCL   comma delimited, not show resources
  --ns-incl NS_INCL     comma delimited, show only resources of specified namespaces
  --ns-excl NS_EXCL     comma delimited, not show resources of specified namespaces
  --trunc TRUNC         Value truncate length
```

## Example

We are going to run a simple container and see what resources are being created and deleted.

Let's start the script, here we leave out the `kube-system` and `kube-node-lease` namespace since they are unrelated here.

```sh
$ ./kubewatch.py --ns-excl kube-system,kube-node-lease
```

Now run a container

```sh
$ kubectl run echo -ti --rm --attach --image=alpine --image-pull-policy=IfNotPresent --restart=Never --command -- echo hello
hello
pod "echo" deleted
```

And the logs are

```
07:53:21.952724  PUT /pods/default/echo
  metadata.labels.run                 echo
  spec.dnsPolicy                      ClusterFirst
  spec.enableServiceLinks             true
  spec.restartPolicy                  Never
  spec.schedulerName                  default-scheduler
  spec.securityContext                {}
  spec.terminationGracePeriodSeconds  30
07:53:21.996132  PUT /pods/default/echo
  metadata.labels.run                 echo
  spec.dnsPolicy                      ClusterFirst
  spec.enableServiceLinks             true
  spec.restartPolicy                  Never
  spec.schedulerName                  default-scheduler
  spec.securityContext                {}
  spec.terminationGracePeriodSeconds  30
07:53:22.000342  PUT /events/default/echo.16171f79f55edd17
  count                               1
  firstTimestamp                      2020-06-10T07:53:21Z
  involvedObject.apiVersion           v1
  involvedObject.kind                 Pod
  involvedObject.name                 echo
  involvedObject.namespace            default
  involvedObject.resourceVersion      3192
  involvedObject.uid                  9cb623b8-c44d-42f5-b655-68094b0a2d45
  lastTimestamp                       2020-06-10T07:53:21Z
  message                             Successfully assigned default/echo to ubuntu-focal
  reason                              Scheduled
  source.component                    default-scheduler
  type                                Normal
07:53:22.003206  PUT /pods/default/echo
  metadata.labels.run                 echo
  spec.dnsPolicy                      ClusterFirst
  spec.enableServiceLinks             true
  spec.restartPolicy                  Never
  spec.schedulerName                  default-scheduler
  spec.securityContext                {}
  spec.terminationGracePeriodSeconds  30
07:53:22.654911  PUT /crd.projectcalico.org/ipamhandles/k8s-pod-network.1f77c04c717ca162e42d7dc83a96bd9808ffab92b28f91304d3d53245d6fca52
  metadata.annotations."projectcalico.org/metadata" {"creationTimestamp":null}
  spec.block."192.168.223.128/26"     1
  spec.handleID                       k8s-pod-network.1f77c04c717ca162e42d7dc83a96bd9808ffab92b28f91304d3d53245d6fca52
07:53:22.662506  PUT /crd.projectcalico.org/ipamblocks/192-168-223-128-26
  metadata.annotations."projectcalico.org/metadata" {"creationTimestamp":null}
  spec.affinity                       host:ubuntu-focal
  spec.allocations                    [0, null, null, null, 1, 2, 3, null, null, 4, null, null, null, null, null, null ...
  spec.attributes                     [{"handle_id": "ipip-tunnel-addr-ubuntu-focal", "secondary": {"node": "ubuntu-fo ...
  spec.cidr                           192.168.223.128/26
  spec.deleted                        false
  spec.strictAffinity                 false
  spec.unallocated                    [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, ...
07:53:22.708711  PUT /pods/default/echo
  metadata.labels.run                 echo
  spec.dnsPolicy                      ClusterFirst
  spec.enableServiceLinks             true
  spec.restartPolicy                  Never
  spec.schedulerName                  default-scheduler
  spec.securityContext                {}
  spec.terminationGracePeriodSeconds  30
07:53:22.744493  PUT /events/default/echo.16171f7a236ebbdb
  count                               1
  firstTimestamp                      2020-06-10T07:53:22Z
  involvedObject.apiVersion           v1
  involvedObject.fieldPath            spec.containers{echo}
  involvedObject.kind                 Pod
  involvedObject.name                 echo
  involvedObject.namespace            default
  involvedObject.resourceVersion      3193
  involvedObject.uid                  9cb623b8-c44d-42f5-b655-68094b0a2d45
  lastTimestamp                       2020-06-10T07:53:22Z
  message                             Container image "alpine" already present on machine
  reason                              Pulled
  source.component                    kubelet
  source.host                         ubuntu-focal
  type                                Normal
07:53:22.795266  PUT /events/default/echo.16171f7a266ce041
  count                               1
  firstTimestamp                      2020-06-10T07:53:22Z
  involvedObject.apiVersion           v1
  involvedObject.fieldPath            spec.containers{echo}
  involvedObject.kind                 Pod
  involvedObject.name                 echo
  involvedObject.namespace            default
  involvedObject.resourceVersion      3193
  involvedObject.uid                  9cb623b8-c44d-42f5-b655-68094b0a2d45
  lastTimestamp                       2020-06-10T07:53:22Z
  message                             Created container echo
  reason                              Created
  source.component                    kubelet
  source.host                         ubuntu-focal
  type                                Normal
07:53:22.903394  PUT /events/default/echo.16171f7a2cf9552e
  count                               1
  firstTimestamp                      2020-06-10T07:53:22Z
  involvedObject.apiVersion           v1
  involvedObject.fieldPath            spec.containers{echo}
  involvedObject.kind                 Pod
  involvedObject.name                 echo
  involvedObject.namespace            default
  involvedObject.resourceVersion      3193
  involvedObject.uid                  9cb623b8-c44d-42f5-b655-68094b0a2d45
  lastTimestamp                       2020-06-10T07:53:22Z
  message                             Started container echo
  reason                              Started
  source.component                    kubelet
  source.host                         ubuntu-focal
  type                                Normal
07:53:23.270904  PUT /pods/default/echo
  metadata.labels.run                 echo
  spec.dnsPolicy                      ClusterFirst
  spec.enableServiceLinks             true
  spec.restartPolicy                  Never
  spec.schedulerName                  default-scheduler
  spec.securityContext                {}
  spec.terminationGracePeriodSeconds  30
07:53:23.434352  PUT /pods/default/echo
  metadata.labels.run                 echo
  spec.dnsPolicy                      ClusterFirst
  spec.enableServiceLinks             true
  spec.restartPolicy                  Never
  spec.schedulerName                  default-scheduler
  spec.securityContext                {}
  spec.terminationGracePeriodSeconds  30
07:53:23.458640  PUT /crd.projectcalico.org/ipamblocks/192-168-223-128-26
  metadata.annotations."projectcalico.org/metadata" {"creationTimestamp":null}
  spec.affinity                       host:ubuntu-focal
  spec.allocations                    [0, null, null, null, 1, 2, 3, null, null, null, null, null, null, null, null, n ...
  spec.attributes                     [{"handle_id": "ipip-tunnel-addr-ubuntu-focal", "secondary": {"node": "ubuntu-fo ...
  spec.cidr                           192.168.223.128/26
  spec.deleted                        false
  spec.strictAffinity                 false
  spec.unallocated                    [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, ...
07:53:23.477261  PUT /crd.projectcalico.org/ipamhandles/k8s-pod-network.1f77c04c717ca162e42d7dc83a96bd9808ffab92b28f91304d3d53245d6fca52
  metadata.annotations."projectcalico.org/metadata" {"creationTimestamp":null}
  spec.block                          {}
  spec.handleID                       k8s-pod-network.1f77c04c717ca162e42d7dc83a96bd9808ffab92b28f91304d3d53245d6fca52
07:53:23.487994  DELETE /pods/default/echo
07:53:23.496890  DELETE /crd.projectcalico.org/ipamhandles/k8s-pod-network.1f77c04c717ca162e42d7dc83a96bd9808ffab92b28f91304d3d53245d6fca52
```

