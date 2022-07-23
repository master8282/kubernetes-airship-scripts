#!/usr/bin/env python

import warnings
import os
import re
import sys
import argparse
import traceback


def obj_del(uid, name, obj_name, del_obj, auto_remove, verbose):

    try:
        if auto_remove:
            del_obj(uid)
            msg = "{} {} {} {}\n".format(obj_name[:-1],
                                         uid, name, "DELETED")
            if verbose:
                sys.stdout.write(msg)
        else:
            msg = "{} {} {} {}\n".format(obj_name[:-1],
                                         uid, name, "SUSPECTED")
            if verbose:
                sys.stdout.write(msg)
    except Exception:
        sys.stderr.write(traceback.format_exc())


def obj_sort(lst, del_obj, obj_type, filt, obj_name,
             auto_remove, verbose, **all_tenants):
    try:
        if obj_type == "isdict":
            for item in lst()[obj_name]:
                if filt and item['name'] and re.search(filt, item['name']):
                    obj_del(item['id'], item['name'], obj_name, del_obj,
                            auto_remove, verbose)
                else:
                    msg = "{} {} {} OK\n".format(obj_name[:-1],
                                                 item['id'], item['name'])
                    if verbose > 1:
                        sys.stdout.write(msg)
        elif obj_type == "islist":
            for item in lst(**all_tenants):
                if filt and item.name and re.search(filt, item.name):
                    obj_del(item.id, item.name, obj_name, del_obj,
                            auto_remove, verbose)
                else:
                    msg = "{} {} {} OK\n".format(obj_name[:-1],
                                                 item.id, item.name)
                    if verbose > 1:
                        sys.stdout.write(msg)
    except Exception:
        sys.stderr.write(traceback.format_exc())


def obj_sort_heat(lst, del_obj, filt, obj_name,
                  auto_remove, verbose, **all_tenants):
    try:
        for item in lst(**all_tenants):
            if filt and item.stack_name and re.search(filt, item.stack_name):
                obj_del(item.id, item.stack_name, obj_name, del_obj,
                        auto_remove, verbose)
            else:
                msg = "{} {} {} OK\n".format(obj_name[:-1],
                                             item.id, item.stack_name)
                if verbose > 1:
                    sys.stdout.write(msg)
    except Exception:
        sys.stderr.write(traceback.format_exc())


def args_init():

    auth_url = os.getenv('OS_AUTH_URL')
    username = os.getenv('OS_USERNAME', 'admin')
    password = os.getenv('OS_PASSWORD')
    project_name = os.getenv('OS_PROJECT_NAME', 'admin')
    user_domain_name = os.getenv('OS_USER_DOMAIN_NAME', 'default')
    project_domain_name = os.getenv('OS_PROJECT_DOMAIN_NAME', 'default')
    parser = argparse.ArgumentParser(description='The script purges the filtered \
                                     post AQuA test resources using \
                                     the filters.')
    parser.add_argument('--os-auth-url', metavar='', default=auth_url,
                        help='Keystone auth endpoint url.')
    parser.add_argument('--os-username', metavar='', default=username,
                        help='User name.')
    parser.add_argument('--os-password', metavar='', default=password,
                        help='User password.')
    parser.add_argument('--os-project-name', metavar='', default=project_name,
                        help='Project name.')
    parser.add_argument('--os-user-domain-name', default=user_domain_name,
                        metavar='', help='User domain name.')
    parser.add_argument('--os-project-domain-name',
                        default=project_domain_name,
                        metavar='', help='User project domain name.')
    parser.add_argument('--net-delete', metavar='',
                        help='Delete specified network using ID.')
    parser.add_argument('--subnet-delete', metavar='',
                        help='Delete specified subnetwork using ID.')
    parser.add_argument('--port-delete', metavar='',
                        help='Delete specified port using ID.')
    parser.add_argument('--secgr-delete', metavar='',
                        help='Delete specified security group using ID.')
    parser.add_argument('--project-delete', metavar='',
                        help='Delete specified project using ID.')
    parser.add_argument('--volume-delete', metavar='',
                        help='Delete specified volume using ID.')
    parser.add_argument('--snapshot-delete', metavar='',
                        help='Delete specified snapshot using ID.')
    parser.add_argument('--vm-delete', metavar='',
                        help='Delete specified VM using ID.')
    parser.add_argument('--flavor-delete', metavar='',
                        help='Delete specified falavor using ID.')
    parser.add_argument('--image-delete', metavar='',
                        help='Delete specified image using ID.')
    parser.add_argument('--stack-delete', metavar='',
                        help='Delete specified stack using ID.')
    parser.add_argument('--verbose', action='store_true',
                        help='Presensts all objects.')
    parser.add_argument('--silent', action='store_true',
                        help='Hides filtered objects output.')
    parser.add_argument('--show-all', action='store_true',
                        help='Displays the list of all filtered resources.')
    parser.add_argument('--show-nets', action='store_true',
                        help='Displays the list of filtered networks.')
    parser.add_argument('--show-subnets', action='store_true',
                        help='Displays the list of filtered subnetworks.')
    parser.add_argument('--show-ports', action='store_true',
                        help='Displays the list of filtered ports.')
    parser.add_argument('--show-secgrs', action='store_true',
                        help='Displays the list of filtered security groups.')
    parser.add_argument('--show-projects', action='store_true',
                        help='Displays the list of filtered projects.')
    parser.add_argument('--show-volumes', action='store_true',
                        help='Displays the list of filtered volumes.')
    parser.add_argument('--show-snapshots', action='store_true',
                        help='Displays the list of filtered snapshots.')
    parser.add_argument('--show-vms', action='store_true',
                        help='Displays the list of filtered vms.')
    parser.add_argument('--show-flavors', action='store_true',
                        help='Displays the list of filtered flavors.')
    parser.add_argument('--show-images', action='store_true',
                        help='Displays the list of filtered images.')
    parser.add_argument('--show-stacks', action='store_true',
                        help='Displays the list of filtered stacks.')
    parser.add_argument('--remove-all', action='store_true',
                        help='Removes all filtered resources automatically. \
Be careful!!! If customers object name matches \
with the filter it will be deleted.')
    parser.add_argument('--remove-nets', action='store_true',
                        help='Removes netvork filtered resources automatically. \
Be careful!!! If customers object name matches \
with the filter it will be deleted.')
    parser.add_argument('--remove-subnets', action='store_true',
                        help='Removes subnetwork filtered resources automatically. \
Be careful!!! If customers object name matches \
with the filter it will be deleted.')
    parser.add_argument('--remove-ports', action='store_true',
                        help='Removes port filtered resources automatically. \
Be careful!!! If customers object name matches \
with the filter it will be deleted.')
    parser.add_argument('--remove-secgrs', action='store_true',
                        help='Removes secgr filtered resources automatically. \
Be careful!!! If customers object name matches \
with the filter it will be deleted.')
    parser.add_argument('--remove-projects', action='store_true',
                        help='Removes project filtered resources automatically. \
Be careful!!! If customers object name matches \
with the filter it will be deleted.')
    parser.add_argument('--remove-volumes', action='store_true',
                        help='Removes volume filtered resources automatically. \
Be careful!!! If customers object name matches \
with the filter it will be deleted.')
    parser.add_argument('--remove-snapshots', action='store_true',
                        help='Removes snapshot filtered resources automatically. \
Be careful!!! If customers object name matches \
with the filter it will be deleted.')
    parser.add_argument('--remove-vms', action='store_true',
                        help='Removes all object resources automatically. \
Be careful!!! If customers object name matches \
with the filter it will be deleted.')
    parser.add_argument('--remove-flavors', action='store_true',
                        help='Removes flavor filtered resources automatically. \
Be careful!!! If customers object name matches \
with the filter it will be deleted.')
    parser.add_argument('--remove-images', action='store_true',
                        help='Removes image filtered resources automatically. \
Be careful!!! If customers object name matches \
with the filter it will be deleted.')
    parser.add_argument('--remove-stacks', action='store_true',
                        help='Removes stack filtered resources automatically. \
Be careful!!! If customers object name matches \
with the filter it will be deleted.')
    return parser.parse_args()


def run():

    filt_net = "(?:^aqua-\w\w\w\w\w\w\w\w-\w*)"
    filt_subnet = "(?:^aqua-\w\w\w\w\w\w\w\w-\w*)"
    filt_port = "(?:^shaker_.*_.*)"
    filt_sec_grp = "(?:^aqua-\w\w\w\w\w\w\w\w-\w*)"
    filt_proj = "(?:[-_]aqua[-_].*)"
    filt_vol = "(?:^aqua-\w\w\w\w\w\w\w\w-\w*)"
    filt_snap = "(?:^aqua-\w\w\w\w\w\w\w\w-\w*)"
    filt_vm = "(?:(^aqua-\w\w\w\w\w\w\w\w-\w*)|(^shaker_\w*_\w*_\w*))"
    filt_flv = "(?:^shaker_.*_.*)"
    filt_img = "(?:^shaker-image$)"
    filt_stack = "(?:(^aqua[-_]\w*[-_]\w*))"

    args = args_init()
    all_tenants = {'search_opts': {'all_tenants': True}}

    check_if_show = any([args.show_all,
                         args.show_nets,
                         args.show_subnets,
                         args.show_ports,
                         args.show_secgrs,
                         args.show_projects,
                         args.show_volumes,
                         args.show_snapshots,
                         args.show_vms,
                         args.show_flavors,
                         args.show_images,
                         args.show_stacks])

    check_if_remove = any([args.remove_all,
                           args.remove_nets,
                           args.remove_subnets,
                           args.remove_ports,
                           args.remove_secgrs,
                           args.remove_projects,
                           args.remove_volumes,
                           args.remove_snapshots,
                           args.remove_vms,
                           args.remove_flavors,
                           args.remove_images])

    check_if_delete = any([args.net_delete,
                           args.subnet_delete,
                           args.port_delete,
                           args.secgr_delete,
                           args.project_delete,
                           args.volume_delete,
                           args.snapshot_delete,
                           args.vm_delete,
                           args.flavor_delete,
                           args.image_delete,
                           args.stack_delete])

    if not args.os_auth_url or not args.os_password:
        msg = "No args '--os-auth-url' or '--os-password' are provided. \
Please use help '-h'.\n"
        sys.stderr.write(msg)
        sys.exit(1)
    if args.verbose and args.silent:
        msg = "Should be select or '--verbose' or '--silent' only.\n"
        sys.stderr.write(msg)
        sys.exit(1)
    if (check_if_show or check_if_delete) and args.silent:
        args.silent = False
    if check_if_show and check_if_remove:
        msg = "Option 'show_*' can not be used with 'remove_*'.\n"
        sys.stderr.write(msg)
        sys.exit(1)
    elif check_if_remove and check_if_delete:
        msg = "Option '--*-delete' can not be used with 'remove_*'.\n"
        sys.stderr.write(msg)
        sys.exit(1)
    elif check_if_delete and check_if_show:
        msg = "Option '--*-delete' can not be used with 'show_*'.\n"
        sys.stderr.write(msg)
        sys.exit(1)
    elif not any([check_if_show, check_if_remove, check_if_delete]):
        msg = "Specify options or use '-h' for help.\n"
        sys.stderr.write(msg)
        sys.exit(1)
    verbose = 1 + args.verbose - args.silent
    auth = v3.Password(user_domain_name=args.os_user_domain_name,
                       username=args.os_username,
                       password=args.os_password,
                       project_domain_name=args.os_project_domain_name,
                       project_name=args.os_project_name,
                       auth_url=args.os_auth_url)
    sess = session.Session(auth=auth, verify=False)
    keystone_get = keystone_client.Client(session=sess)
    neutron_get = neutron_client.Client(session=sess)
    cinder_get = cinder_client.Client(session=sess)
    nova_get = nova_client.Client('2.0', session=sess)
    glance_get = glance_client.Client(session=sess)
    heat_get = heat_client.Client(session=sess)

    nets = neutron_get.list_networks
    subnets = neutron_get.list_subnets
    ports = neutron_get.list_ports
    sec_grps = neutron_get.list_security_groups
    projs = keystone_get.projects.list
    vols = cinder_get.volumes.list
    snaps = cinder_get.volume_snapshots.list
    vms = nova_get.servers.list
    flvs = nova_get.flavors.list
    imgs = glance_get.images.list
    stacks = heat_get.stacks.list

    del_net = neutron_get.delete_network
    del_subnet = neutron_get.delete_subnet
    del_port = neutron_get.delete_port
    del_sec_grp = neutron_get.delete_security_group
    del_proj = keystone_get.projects.delete
    del_vol = cinder_get.volumes.delete
    del_snap = cinder_get.volume_snapshots.delete
    del_vm = nova_get.servers.delete
    del_flv = nova_get.flavors.delete
    del_img = glance_get.images.delete
    del_stack = heat_get.stacks.delete

    print("\n-------------------------\n")

    if args.show_all:
        auto_remove = 0
        obj_sort(nets, del_net, "isdict", filt_net, "networks",
                 auto_remove, verbose)
        obj_sort(subnets, del_subnet, "isdict", filt_subnet, "subnets",
                 auto_remove, verbose)
        obj_sort(ports, del_port, "isdict", filt_port, "ports",
                 auto_remove, verbose)
        obj_sort(sec_grps, del_sec_grp, "isdict", filt_sec_grp,
                 "security_groups", auto_remove, verbose)
        obj_sort(projs, del_proj, "islist", filt_proj, "projects",
                 auto_remove, verbose)
        obj_sort(vols, del_vol, "islist", filt_vol, "volumes",
                 auto_remove, verbose, **all_tenants)
        obj_sort(snaps, del_snap, "islist", filt_snap, "snapshots",
                 auto_remove, verbose, **all_tenants)
        obj_sort(vms, del_vm, "islist", filt_vm, "servers",
                 auto_remove, verbose, **all_tenants)
        obj_sort(flvs, del_flv, "islist", filt_flv, "flavors",
                 auto_remove, verbose)
        obj_sort(imgs, del_img, "islist", filt_img, "images",
                 auto_remove, verbose, **all_tenants)
        obj_sort_heat(stacks, del_stack, filt_stack, "stacks",
                      auto_remove, verbose, **all_tenants)

    elif check_if_show:
        auto_remove = 0
        if args.show_nets:
            obj_sort(nets, del_net, "isdict", filt_net, "networks",
                     auto_remove, verbose)
        if args.show_subnets:
            obj_sort(subnets, del_subnet, "isdict", filt_subnet, "subnets",
                     auto_remove, verbose)
        if args.show_ports:
            obj_sort(ports, del_port, "isdict", filt_port, "ports",
                     auto_remove, verbose)
        if args.show_secgrs:
            obj_sort(sec_grps, del_sec_grp, "isdict", filt_sec_grp,
                     "security_groups", auto_remove, verbose)
        if args.show_projects:
            obj_sort(projs, del_proj, "islist", filt_proj, "projects",
                     auto_remove, verbose)
        if args.show_volumes:
            obj_sort(vols, del_vol, "islist", filt_vol, "volumes",
                     auto_remove, verbose, **all_tenants)
        if args.show_snapshots:
            obj_sort(snaps, del_snap, "islist", filt_snap, "snapshots",
                     auto_remove, verbose, **all_tenants)
        if args.show_vms:
            obj_sort(vms, del_vm, "islist", filt_vm, "servers",
                     auto_remove, verbose, **all_tenants)
        if args.show_flavors:
            obj_sort(flvs, del_flv, "islist", filt_flv, "flavors",
                     auto_remove, verbose)
        if args.show_images:
            obj_sort(imgs, del_img, "islist", filt_img, "images",
                     auto_remove, verbose, **all_tenants)
        if args.show_stacks:
            obj_sort_heat(stacks, del_stack, filt_stack, "stacks",
                          auto_remove, verbose, **all_tenants)

    elif args.remove_all:
        auto_remove = 1
        obj_sort_heat(stacks, del_stack, filt_stack, "stacks",
                      auto_remove, verbose, **all_tenants)
        obj_sort(nets, del_net, "isdict", filt_net, "networks",
                 auto_remove, verbose)
        obj_sort(subnets, del_subnet, "isdict", filt_subnet, "subnets",
                 auto_remove, verbose)
        obj_sort(ports, del_port, "isdict", filt_port, "ports",
                 auto_remove, verbose)
        obj_sort(sec_grps, del_sec_grp, "isdict", filt_sec_grp,
                 "security_groups", auto_remove, verbose)
        obj_sort(projs, del_proj, "islist", filt_proj, "projects",
                 auto_remove, verbose)
        obj_sort(vols, del_vol, "islist", filt_vol, "volumes",
                 auto_remove, verbose, **all_tenants)
        obj_sort(snaps, del_snap, "islist", filt_snap, "snapshots",
                 auto_remove, verbose, **all_tenants)
        obj_sort(vms, del_vm, "islist", filt_vm, "servers",
                 auto_remove, verbose, **all_tenants)
        obj_sort(flvs, del_flv, "islist", filt_flv, "flavors",
                 auto_remove, verbose)
        obj_sort(imgs, del_img, "islist", filt_img, "images",
                 auto_remove, verbose, **all_tenants)

    elif check_if_remove:
        auto_remove = 1
        if args.remove_nets:
            obj_sort(nets, del_net, "isdict", filt_net, "networks",
                     auto_remove, verbose)
        if args.remove_subnets:
            obj_sort(subnets, del_subnet, "isdict", filt_subnet, "subnets",
                     auto_remove, verbose)
        if args.remove_ports:
            obj_sort(ports, del_port, "isdict", filt_port, "ports",
                     auto_remove, verbose)
        if args.remove_secgrs:
            obj_sort(sec_grps, del_sec_grp, "isdict", filt_sec_grp,
                     "security_groups", auto_remove, verbose)
        if args.remove_projects:
            obj_sort(projs, del_proj, "islist", filt_proj, "projects",
                     auto_remove, verbose)
        if args.remove_volumes:
            obj_sort(vols, del_vol, "islist", filt_vol, "volumes",
                     auto_remove, verbose, **all_tenants)
        if args.remove_snapshots:
            obj_sort(snaps, del_snap, "islist", filt_snap, "snapshots",
                     auto_remove, verbose, **all_tenants)
        if args.remove_vms:
            obj_sort(vms, del_vm, "islist", filt_vm, "servers",
                     auto_remove, verbose, **all_tenants)
        if args.remove_flavors:
            obj_sort(flvs, del_flv, "islist", filt_flv, "flavors",
                     auto_remove, verbose)
        if args.remove_images:
            obj_sort(imgs, del_img, "islist", filt_img, "images",
                     auto_remove, verbose, **all_tenants)
        if args.remove_stacks:
            obj_sort_heat(stacks, del_stack, filt_stack, "stacks",
                          auto_remove, verbose, **all_tenants)

    elif check_if_delete:
        auto_remove = 1
        for key in ['net_delete',
                    'subnet_delete',
                    'port_delete',
                    'secgr_delete',
                    'project_delete',
                    'volume_delete',
                    'snapshot_delete',
                    'vm_delete',
                    'flavor_delete',
                    'image_delete',
                    'stack_delete']:

            if isinstance(args.__dict__[key], str):
                args.__dict__[key] = tuple(args.__dict__[key].split(","))
            elif not isinstance(args.__dict__[key], (tuple, type(None), list)):
                msg = "Wrong argument type {}.\n".format(args.__dict__[key])
                sys.stderr.write(msg)
                sys.exit(1)

        if args.net_delete:
            for uid in args.net_delete:
                obj_del(uid, "", "networks", del_net, auto_remove, verbose)
        if args.subnet_delete:
            for uid in args.subnet_delete:
                obj_del(uid, "", "subnets", del_subnet, auto_remove, verbose)
        if args.port_delete:
            for uid in args.port_delete:
                obj_del(uid, "", "ports", del_port, auto_remove, verbose)
        if args.secgr_delete:
            for uid in args.secgr_delete:
                obj_del(uid, "", "security groups",
                        del_sec_grp, auto_remove, verbose)
        if args.project_delete:
            for uid in args.secgr_delete:
                obj_del(uid, "", "projects",
                        del_sec_grp, auto_remove, verbose)
        if args.volume_delete:
            for uid in args.volume_delete:
                obj_del(uid, "", "volumes", del_vol, auto_remove, verbose)
        if args.snapshot_delete:
            for uid in args.volume_delete:
                obj_del(uid, "", "snapshots", del_snap, auto_remove, verbose)
        if args.vm_delete:
            for uid in args.vm_delete:
                obj_del(uid, "", "vms", del_vm, auto_remove, verbose)
        if args.flavor_delete:
            for uid in args.flavor_delete:
                obj_del(uid, "", "flavors", del_flv, auto_remove, verbose)
        if args.image_delete:
            for uid in args.image_delete:
                obj_del(uid, "", "images", del_img, auto_remove, verbose)
        if args.stack_delete:
            for uid in args.stack_delete:
                obj_del(uid, "", "stacks", del_stack, auto_remove, verbose)

    print("\nScript finished.\n")


if __name__ == "__main__":
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        from keystoneclient.v3 import client as keystone_client
        from keystoneauth1.identity import v3
        from keystoneauth1 import session
        from neutronclient.v2_0 import client as neutron_client
        from cinderclient.v3 import client as cinder_client
        from novaclient import client as nova_client
        from glanceclient.v2 import client as glance_client
        from heatclient.v1 import client as heat_client
        run()
