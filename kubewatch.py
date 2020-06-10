#!/usr/bin/python3

import os
import shlex
import ssl
import json
from datetime import datetime
from urllib.parse import urlparse
from http.client import HTTPSConnection
from subprocess import Popen, PIPE


def sh_stream(cmd):
    process = Popen(shlex.split(cmd), stdout=PIPE, universal_newlines=True)
    while True:
        output = process.stdout.readline()
        if output:
            yield output.rstrip()
        if process.poll() is not None:
            break


def get_etcd_container(pod):
    cmd = """
    kubectl get pod {} -n kube-system -o jsonpath='{{.status.containerStatuses[0].containerID}}' | tr -s '//' ' ' | cut -d" " -f2
    """.format(
        pod
    )
    return os.popen(cmd).read().strip()


def records(pod):
    container_id = get_etcd_container(pod)
    cmd = """
    docker exec -i {} etcdctl --key /etc/kubernetes/pki/etcd/ca.key --cert /etc/kubernetes/pki/etcd/ca.crt --insecure-skip-tls-verify watch --prefix "/registry" -w fields
    """.format(
        container_id
    )
    verb = None
    for line in sh_stream(cmd):
        if line.startswith('"Type"'):
            verb = line.split(":")[1].strip()
        elif line.startswith('"Key"'):
            key = line.split(":")[1].strip().replace('"', "")
            ## etcd key format is /registry[/services]/<resource>/<namespace>/<name>
            yield verb, key.split("/")[-3:]


def get_sa_token(serviceaccount):
    cmd = """
    kubectl get secrets $(kubectl get sa {} -o jsonpath='{{.secrets[0].name}}') -o jsonpath='{{.data.token}}' | base64 -d
    """.format(
        serviceaccount
    )
    return os.popen(cmd).read().strip()


def get_server(cluster):
    cmd = """
    kubectl config view -o jsonpath='{{.clusters[?(@.name=="{}")].cluster.server}}'
    """.format(
        cluster
    )
    res = urlparse(os.popen(cmd).read().strip())
    return res.hostname, res.port


class APIConn(object):
    def __init__(self, cluster, serviceaccount):
        host, port = get_server(cluster)
        self.conn = HTTPSConnection(
            host, port, context=ssl._create_unverified_context()
        )
        self.headers = {
            "Authorization": "Bearer {}".format(get_sa_token(serviceaccount))
        }

    def request(self, method, path):
        self.conn.request(method, path, headers=self.headers)
        return self.conn.getresponse()


def extract_managed_fields(acc, path, body, fields):
    for k, v in fields.items():
        if not k.startswith("f:"):
            continue
        k = k[2:]
        key = '"' + k + '"' if "." in k else k
        if len(v) == 0:
            acc.append([".".join(path + [key]), body[k]])
        else:
            extract_managed_fields(acc, path + [key], body[k], v)


def handle_resp(resp):
    body = resp.read()
    if resp.status == 200:
        body1 = json.loads(body)
        fields = body1["metadata"]["managedFields"][0]["fieldsV1"]
        acc = []
        extract_managed_fields(acc, [], body1, fields)
        return acc
    else:
        return []


def api_path(resource, ns, name):
    if resource == "leases":
        return "/apis/coordination.k8s.io/v1/namespaces/{}/leases/{}".format(ns, name)
    if resource == "crd.projectcalico.org":
        return "/apis/crd.projectcalico.org/v1/{}/{}".format(ns, name)

    return "/api/v1/namespaces/{}/{}/{}".format(ns, resource, name)


def main(args):
    ns_incl = set(filter(None, args.ns_incl.split(",")))
    ns_excl = set(filter(None, args.ns_excl.split(",")))
    res_incl = set(filter(None, args.res_incl.split(",")))
    res_excl = set(filter(None, args.res_excl.split(",")))

    conn = APIConn(args.cluster, args.serviceaccount)
    for v, k in records(args.etcd_pod):
        res, ns, name = k
        if ns == "masterleases":
            continue
        if res_incl and res not in res_incl:
            continue
        if res_excl and res in res_excl:
            continue
        if ns_incl and ns not in ns_incl:
            continue
        if ns_excl and ns in ns_excl:
            continue

        dt = datetime.now().strftime("%H:%M:%S.%f")
        print("{:16s} {} {}".format(dt, v, "/" + "/".join(k)))

        if v == "PUT":
            resp = conn.request("GET", api_path(res, ns, name))
            vals = handle_resp(resp)
            for k, v in vals:
                if not isinstance(v, str):
                    v = json.dumps(v)
                if len(v) > args.trunc:
                    v = v[: args.trunc] + " ..."
                print("  {:35s} {}".format(k, v))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Watch kubernetes resources")
    parser.add_argument("--etcd-pod", default="etcd-ubuntu-focal", help="pod of etcd")
    parser.add_argument("--cluster", default="kubernetes", help="cluster to watch")
    parser.add_argument(
        "--serviceaccount", default="resource-reader", help="Service Account"
    )
    parser.add_argument(
        "--res-incl", default="", help="comma delimited, show only resources",
    )
    parser.add_argument(
        "--res-excl", default="", help="comma delimited, not show resources",
    )
    parser.add_argument(
        "--ns-incl",
        default="",
        help="comma delimited, show only resources of specified namespaces",
    )
    parser.add_argument(
        "--ns-excl",
        default="",
        help="comma delimited, not show resources of specified namespaces",
    )
    parser.add_argument("--trunc", type=int, default=80, help="Value truncate length")
    args = parser.parse_args()
    main(args)
