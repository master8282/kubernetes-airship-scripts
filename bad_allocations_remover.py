#!/usr/bin/env python3

import os
import sys
import argparse
import warnings
import traceback


class osc_client():
    _api_version = dict(placement='1')
    _region_name = None
    interface = 'public'
    session = None


def args_init():
    auth_url = os.getenv('OS_AUTH_URL')
    username = os.getenv('OS_USERNAME', 'admin')
    password = os.getenv('OS_PASSWORD')
    project_name = os.getenv('OS_PROJECT_NAME', 'admin')
    user_domain_name = os.getenv('OS_USER_DOMAIN_NAME', 'default')
    project_domain_name = os.getenv('OS_PROJECT_DOMAIN_NAME', 'default')
    parser = argparse.ArgumentParser(description='The script purges the \
    filtered post AQuA test resources using the filters.')
    parser.add_argument('--os-auth-url', metavar='', default=auth_url,
                        help='Keystone auth endpoint url.')
    parser.add_argument('--os-username', metavar='', default=username,
                        help='User name.')
    parser.add_argument('--os-password', metavar='', default=password,
                        help='User password.')
    parser.add_argument('--os-project-name', metavar='', default=project_name,
                        help='Project name.')
    parser.add_argument('--os-user-domain-name',
                        default=user_domain_name,
                        metavar='', help='User domain name.')
    parser.add_argument('--os-project-domain-name',
                        default=project_domain_name,
                        metavar='', help='User project domain name.')
    parser.add_argument('--delete', action='store_true',
                        help='Deletes the allocation.')
    parser.add_argument('--show', action='store_true',
                        help='Shows all allocations.')
    parser.add_argument('--silent', action='store_true',
                        help='Hides the output.')
    parser.add_argument('--remove-all', action='store_true',
                        help='Removes all allocations automatically.')
    parser.add_argument('--provider-uuid', metavar='',
                        help='The UUID of provider.')
    parser.add_argument('--vm-uuid', metavar='',
                        help='The UUID of vm/server.')
    return parser.parse_args()


def osc_request(method, url):
    return make_client(osc_client).request(method, url,
                                           params={'required': []}).json()


def osc_del(args, prov_id, vm_id):
    try:
        args = ["--os-auth-url", args.os_auth_url,
                "--os-password", args.os_password,
                "--os-username", args.os_username,
                "--os-project-name", args.os_project_name,
                "--os-user-domain-name", args.os_user_domain_name,
                "--os-project-domain-name", args.os_project_domain_name,
                "resource", "provider", "allocation", "unset",
                "--provider", prov_id, vm_id]
        OpenStackShell().run(args)
    except Exception:
        sys.stderr.write(traceback.format_exc())
    msg = "Allocation of {} has been deleted.\n".format(vm_id)
    return msg


def run():
    args = args_init()
    verbose = True
    autoremove = False
    if args.remove_all:
        autoremove = True
    if args.silent:
        verbose = False
    if args.delete:
        if args.silent:
            sys.stdout.write("'--silent' will be ignored.\n")
        if not args.provider_uuid or not args.vm_uuid:
            msg = "Please specify '--provider-uuid' and '--vm-uuid'."
            sys.stdout.write(msg)
        else:
            if isinstance(args.vm_uuid, str):
                args.vm_uuid = tuple(args.vm_uuid.split(','))
            elif not isinstance(args.vm_uuid, (tuple, type(None), list)):
                msg = "Wrong argument type {}.\n".format(args.vm_uuid)
            for item in args.vm_uuid:
                msg = osc_del(args, args.provider_uuid, item)
                sys.stdout.write(msg)

    elif args.show or args.remove_all:
        if args.silent and not args.remove_all:
            sys.stdout.write("'--silent' will be ignored.\n")
            verbose = True
        all_allocated = dict()

        auth = v3.Password(user_domain_name=args.os_user_domain_name,
                           username=args.os_username,
                           password=args.os_password,
                           project_domain_name=args.os_project_domain_name,
                           project_name=args.os_project_name,
                           auth_url=args.os_auth_url)
        sess = session.Session(auth=auth, verify=False)
        osc_client.session = sess

        all_vms = (nova_client.Client('2.0', session=sess)
                   .servers.list(search_opts={'all_tenants': True}))
        all_vm_ids = {vm_id.id for vm_id in all_vms}
        all_res_prov = osc_request('GET', '/resource_providers')
        all_res_prov_ids = set(item['uuid'] for item in all_res_prov
                               ['resource_providers'])
        for prov_id in all_res_prov_ids:
            general = osc_request('GET', "/resource_providers/{}"
                                  .format(prov_id))
            alloc = osc_request('GET', "/resource_providers/{}/allocations"
                                .format(prov_id))

            if alloc['allocations']:
                for vm_id in alloc['allocations']:
                    vm_uuid = vm_id
                    vcpu = alloc['allocations'][vm_id]['resources']['VCPU']
                    mem = alloc['allocations'][vm_id]['resources']['MEMORY_MB']
                    disk = alloc['allocations'][vm_id]['resources']['DISK_GB']
                all_allocated.update({vm_uuid: {'vcpu': vcpu, 'mem': mem,
                                                'disk': disk,
                                                'prov_uuid': general['uuid'],
                                                'prov_name': general['name']}})
        found = set(all_allocated).difference(all_vm_ids)
        msg = ("\n{}\t\t\t\t\t{}\t{}\t{}\t{}\t\t\t\t{}\n"
               .format('VM_UUID', 'CPU', 'RAM', 'DISK',
                       'PROVIDER_UUID', 'HOST NAME'))
        if verbose > 0:
            sys.stdout.write(msg)

        for item in found:
            msg = ("{}\t{}\t{}\t{}\t{}\t{}\n".format(item,
                   all_allocated[item]['vcpu'],
                   all_allocated[item]['mem'],
                   all_allocated[item]['disk'],
                   all_allocated[item]['prov_uuid'],
                   all_allocated[item]['prov_name']))
            if verbose:
                sys.stdout.write(msg)
            if autoremove:
                msg = osc_del(args, all_allocated[item]['prov_uuid'], item)
                if verbose:
                    sys.stdout.write(msg)
        if verbose:
            sys.stdout.write("\nScript finished.\n")
    else:
        msg = "Please specify argumets or use '--help'."
        sys.stdout.write(msg)


if __name__ == "__main__":

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        from keystoneauth1.identity import v3
        from keystoneauth1 import session
        from osc_placement.plugin import make_client
        from novaclient import client as nova_client
        from openstackclient.shell import OpenStackShell
        run()
