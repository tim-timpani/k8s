import argparse
import json
import base64

import invoke
from tabulate import tabulate


def get_args():

    args = argparse.ArgumentParser(description="Kubernetes Utility")
    sub_parser = args.add_subparsers(help='Operation')

    # Load subargs
    parser_load = sub_parser.add_parser('env', help='Print pod/container environment')
    parser_load.set_defaults(operation='env')

    return args.parse_args()


def print_container_env(args: argparse.PARSER):
    secrets = get_secrets()
    table_header = ('NAMESPACE', 'POD', 'NAME', 'VALUE')
    table_details = []
    result = invoke.run('kubectl get pods -A -o json', hide=True)
    pod_data = json.loads(result.stdout)
    for pod in pod_data['items']:
        metadata = pod.get('metadata', {})
        labels = metadata.get('labels', {})
        managed_by = labels.get("app.kubernetes.io/managed-by")
        if managed_by != "Helm":
            continue
        pod_name = metadata.get('name', "")
        namespace = metadata.get('namespace', "")
        spec = pod.get('spec', {})
        containers = spec.get('containers', [])
        for container in containers:
            for env in container.get('env', []):
                env_name = env.get("name", "")
                env_value = env.get("value")
                if env_value is None:
                    value_from = env.get("valueFrom", {})
                    key_ref = value_from.get("secretKeyRef", {})
                    secret_key = key_ref.get("key")
                    secret_name = key_ref.get("name")
                    env_value = secrets.get((namespace, secret_name, secret_key))
                if env_value is not None:
                    table_details.append((namespace, pod_name, env_name, env_value))
            for port in container.get('ports', []):
                port_number = "{}/{}".format(port.get("protocol", ""), port.get("containerPort", ""))
                port_name = "{} port".format(port.get("name", ""))
                table_details.append((namespace, pod_name, port_name, port_number))

    if len(table_details) > 0:
        print(tabulate(table_details, table_header, tablefmt='pretty'))
    else:
        print("No environment found")


def get_secrets():
    secrets = {}
    result = invoke.run('kubectl get secrets -A -o json', hide=True)
    secret_data = json.loads(result.stdout)
    for secret in secret_data['items']:
        metadata = secret.get('metadata', {})
        name = metadata.get('name')
        namespace = metadata.get('namespace')
        for key, value in secret['data'].items():
            secrets[(namespace, name, key)] = base64.b64decode(value).decode('utf-8')
    return secrets


def main():
    args = get_args()
    if args.operation == "env":
        print_container_env(args)
    else:
        raise RuntimeError(f"Operation '{args.operation}' not supported")


if __name__ == "__main__":
    main()
