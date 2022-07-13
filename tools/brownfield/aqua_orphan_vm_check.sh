#!/bin/bash

filter='shaker\|aqua'
kube_cong='--kubeconfig=/etc/kubernetes/admin/kubeconfig.yaml'
mysql_conf='/etc/mysql/admin_user.cnf'
mysql_pod='mariadb-server-0'

if [[ "$1" == "help" ]]
  then
  echo -e "'show'   - The list of the found instances."
  echo -e "'delete' - It purges VM from the libvirt pod."
  echo -e "           Example './aqua_orphan_vm_check.sh libvirt-libvirt-default-2jtks \
instance-0000038f'"

elif [[ "$1" == "show" ]]
  then
  echo -e ""
  echo -e "The following VMs with name pattern \"${filter}\" don't have records in the DB\n"
  echo -e "POD NAME\t\t\tHOST NAME\tVIRSH NAME\t\tUUID\t\t\t\t\tINST NAME"
  echo -e "------------------------------------------------------------------------\
-----------------------------------------------------------"
  pods=$(kubectl $kube_conf get pods -n openstack -l component=libvirt --no-headers -o \
custom-columns=":metadata.name")
  for pod in $pods
  do vm_info=$(kubectl $kube_conf -n openstack exec -i $pod -- /bin/bash -c \
"vms=\$(virsh list --all | awk '/instance-/ {print \$2}')
    for vm in \$vms
    do
    echo $pod \$(hostname) \$vm \$(virsh dumpxml \$vm | awk -F'>|<' \
'/nova:name|<uuid>/ {print \$3}')
    done")
    while read line
    do
    pod_name=$(echo ${line} | awk '{print $1}')
    host_name=$(echo ${line} | awk '{print $2}')
    vm_name=$(echo ${line} | awk '{print $3}')
    uuid=$(echo ${line} | awk '{print $4}')
    name=$(echo ${line} | awk '{print $5}' | grep $filter)
    if [[ "$name" != "" ]]
    then
    mysql_check=$(kubectl $kube_conf -n openstack exec -i $mysql_pod -- /bin/bash -c \
"mysql --defaults-file=$mysql_conf --skip-column-names -s -r -e \"select deleted \
from nova.instances where uuid='$uuid';\"")
      if [[ $mysql_check != 0 ]]
      then
      echo -e $pod_name'\t'$host_name'\t'$vm_name'\t'$uuid'\t'$name
      fi
    fi
    done < <(echo "$vm_info")
  done
  echo -e "Script finished"

elif [[ "$1" == "delete" ]]
  then
  if [ -z "$2" ] || [ -z "$3" ]
    then
    echo -e "Not enough arguments, please use help"
  else
    kubectl --kubeconfig=/etc/kubernetes/admin/kubeconfig.yaml -n openstack \
exec -it $2 -- virsh undefine $3
    sleep 2
    kubectl --kubeconfig=/etc/kubernetes/admin/kubeconfig.yaml -n openstack \
exec -it $2 -- virsh destroy $3
  fi
else
  echo -e "Not enough arguments, please use help"
fi
