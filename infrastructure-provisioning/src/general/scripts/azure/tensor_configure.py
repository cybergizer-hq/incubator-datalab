#!/usr/bin/python

# *****************************************************************************
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
# ******************************************************************************

import logging
import json
import sys
import traceback
import dlab.fab
import dlab.actions_lib
import dlab.meta_lib
import os
import traceback
from fabric.api import *


if __name__ == "__main__":
    instance_class = 'notebook'
    local_log_filename = "{}_{}_{}.log".format(os.environ['conf_resource'], os.environ['project_name'],
                                               os.environ['request_id'])
    local_log_filepath = "/logs/" + os.environ['conf_resource'] + "/" + local_log_filename
    logging.basicConfig(format='%(levelname)-8s [%(asctime)s]  %(message)s',
                        level=logging.DEBUG,
                        filename=local_log_filepath)

    try:
        AzureMeta = dlab.meta_lib.AzureMeta()
        AzureActions = dlab.actions_lib.AzureActions()
        notebook_config = dict()
        try:
            notebook_config['exploratory_name'] = os.environ['exploratory_name'].lower()
        except:
            notebook_config['exploratory_name'] = ''
        notebook_config['service_base_name'] = os.environ['conf_service_base_name']
        notebook_config['resource_group_name'] = os.environ['azure_resource_group_name']
        notebook_config['instance_size'] = os.environ['azure_notebook_instance_size']
        notebook_config['key_name'] = os.environ['conf_key_name']
        notebook_config['user_name'] = os.environ['edge_user_name'].lower()
        notebook_config['project_name'] = os.environ['project_name'].lower()
        notebook_config['endpoint_name'] = os.environ['endpoint_name'].lower()
        notebook_config['project_tag'] = notebook_config['project_name']
        notebook_config['endpoint_tag'] = notebook_config['endpoint_name']
        notebook_config['user_keyname'] = notebook_config['project_name']
        notebook_config['instance_name'] = '{}-{}-{}-nb-{}'.format(notebook_config['service_base_name'],
                                                                   notebook_config['project_name'],
                                                                   notebook_config['endpoint_name'],
                                                                   notebook_config['exploratory_name'])
        notebook_config['image_enabled'] = os.environ['conf_image_enabled']
        notebook_config['shared_image_enabled'] = os.environ['conf_shared_image_enabled']
        if notebook_config['shared_image_enabled'] == 'false':
            notebook_config['expected_image_name'] = '{0}-{1}-{2}-{3}-notebook-image'.format(
                notebook_config['service_base_name'],
                notebook_config['project_name'],
                notebook_config['endpoint_name'],
                os.environ['application'])
            notebook_config['image_tags'] = {"Name": notebook_config['instance_name'],
                                             "SBN": notebook_config['service_base_name'],
                                             "User": notebook_config['user_name'],
                                             "project_tag": notebook_config['project_tag'],
                                             "endpoint_tag": notebook_config['endpoint_tag'],
                                             "Exploratory": notebook_config['exploratory_name'],
                                             os.environ['conf_billing_tag_key']: os.environ['conf_billing_tag_value']}
        else:
            notebook_config['expected_image_name'] = '{0}-{1}-{2}-notebook-image'.format(
                notebook_config['service_base_name'],
                notebook_config['endpoint_name'],
                os.environ['application'])
            notebook_config['image_tags'] = {"Name": notebook_config['instance_name'],
                                             "SBN": notebook_config['service_base_name'],
                                             "User": notebook_config['user_name'],
                                             "endpoint_tag": notebook_config['endpoint_tag'],
                                             "Exploratory": notebook_config['exploratory_name'],
                                             os.environ['conf_billing_tag_key']: os.environ['conf_billing_tag_value']}
        notebook_config['notebook_image_name'] = str(os.environ.get('notebook_image_name'))
        notebook_config['security_group_name'] = '{}-{}-{}-nb-sg'.format(notebook_config['service_base_name'],
                                                                         notebook_config['project_name'],
                                                                         notebook_config['endpoint_name'])
        notebook_config['dlab_ssh_user'] = os.environ['conf_os_user']
        notebook_config['tags'] = {"Name": notebook_config['instance_name'],
                                   "SBN": notebook_config['service_base_name'],
                                   "User": notebook_config['user_name'],
                                   "project_tag": notebook_config['project_tag'],
                                   "endpoint_tag": notebook_config['endpoint_tag'],
                                   "Exploratory": notebook_config['exploratory_name'],
                                   os.environ['conf_billing_tag_key']: os.environ['conf_billing_tag_value']}
        notebook_config['ip_address'] = AzureMeta.get_private_ip_address(notebook_config['resource_group_name'],
                                                                         notebook_config['instance_name'])

        # generating variables regarding EDGE proxy on Notebook instance
        instance_hostname = AzureMeta.get_private_ip_address(notebook_config['resource_group_name'],
                                                             notebook_config['instance_name'])
        edge_instance_name = '{0}-{1}-{2}-edge'.format(notebook_config['service_base_name'],
                                                     notebook_config['project_name'],
                                                     notebook_config['endpoint_name'])
        edge_instance_private_hostname = AzureMeta.get_private_ip_address(notebook_config['resource_group_name'],
                                                                          edge_instance_name)
        if os.environ['conf_network_type'] == 'private':
            edge_instance_hostname = AzureMeta.get_private_ip_address(notebook_config['resource_group_name'],
                                                                      edge_instance_name)
        else:
            edge_instance_hostname = AzureMeta.get_instance_public_ip_address(notebook_config['resource_group_name'],
                                                                              edge_instance_name)
        keyfile_name = "{}{}.pem".format(os.environ['conf_key_dir'], os.environ['conf_key_name'])
        edge_hostname = AzureMeta.get_private_ip_address(notebook_config['resource_group_name'],
                                                         edge_instance_name)

        if os.environ['conf_os_family'] == 'debian':
            notebook_config['initial_user'] = 'ubuntu'
            notebook_config['sudo_group'] = 'sudo'
        if os.environ['conf_os_family'] == 'redhat':
            notebook_config['initial_user'] = 'ec2-user'
            notebook_config['sudo_group'] = 'wheel'
    except Exception as err:
        dlab.fab.append_result("Failed to generate variables dictionary", str(err))
        AzureActions.remove_instance(notebook_config['resource_group_name'], notebook_config['instance_name'])
        sys.exit(1)

    try:
        logging.info('[CREATING DLAB SSH USER]')
        print('[CREATING DLAB SSH USER]')
        params = "--hostname {} --keyfile {} --initial_user {} --os_user {} --sudo_group {}".format(
            instance_hostname, os.environ['conf_key_dir'] + os.environ['conf_key_name'] + ".pem",
            notebook_config['initial_user'], notebook_config['dlab_ssh_user'], notebook_config['sudo_group'])

        try:
            local("~/scripts/{}.py {}".format('create_ssh_user', params))
        except:
            traceback.print_exc()
            raise Exception
    except Exception as err:
        dlab.fab.append_result("Failed creating ssh user 'dlab'.", str(err))
        AzureActions.remove_instance(notebook_config['resource_group_name'], notebook_config['instance_name'])
        sys.exit(1)

    # configuring proxy on Notebook instance
    try:
        logging.info('[CONFIGURE PROXY ON TENSOR INSTANCE]')
        print('[CONFIGURE PROXY ON TENSOR INSTANCE]')
        additional_config = {"proxy_host": edge_instance_private_hostname, "proxy_port": "3128"}
        params = "--hostname {} --instance_name {} --keyfile {} --additional_config '{}' --os_user {}"\
            .format(instance_hostname, notebook_config['instance_name'], keyfile_name, json.dumps(additional_config),
                    notebook_config['dlab_ssh_user'])
        try:
            local("~/scripts/{}.py {}".format('common_configure_proxy', params))
        except:
            traceback.print_exc()
            raise Exception
    except Exception as err:
        dlab.fab.append_result("Failed to configure proxy.", str(err))
        AzureActions.remove_instance(notebook_config['resource_group_name'], notebook_config['instance_name'])
        sys.exit(1)

    # updating repositories & installing python packages
    try:
        logging.info('[INSTALLING PREREQUISITES TO TENSOR NOTEBOOK INSTANCE]')
        print('[INSTALLING PREREQUISITES TO TENSOR NOTEBOOK INSTANCE]')
        params = "--hostname {} --keyfile {} --user {} --region {} --edge_private_ip {}".\
            format(instance_hostname, keyfile_name, notebook_config['dlab_ssh_user'], os.environ['azure_region'],
                   edge_instance_private_hostname)
        try:
            local("~/scripts/{}.py {}".format('install_prerequisites', params))
        except:
            traceback.print_exc()
            raise Exception
    except Exception as err:
        dlab.fab.append_result("Failed installing apps: apt & pip.", str(err))
        AzureActions.remove_instance(notebook_config['resource_group_name'], notebook_config['instance_name'])
        sys.exit(1)

    # installing and configuring TensorFlow and all dependencies
    try:
        logging.info('[CONFIGURE TENSORFLOW NOTEBOOK INSTANCE]')
        print('[CONFIGURE TENSORFLOW NOTEBOOK INSTANCE]')
        params = "--hostname {0} --keyfile {1} " \
                 "--region {2} --os_user {3} " \
                 "--ip_adress {4} --exploratory_name {5} --edge_ip {6}" \
                 .format(instance_hostname, keyfile_name,
                         os.environ['azure_region'], notebook_config['dlab_ssh_user'],
                         notebook_config['ip_address'], notebook_config['exploratory_name'], edge_hostname)
        try:
            local("~/scripts/{}.py {}".format('configure_tensor_node', params))
            dlab.actions_lib.remount_azure_disk(True, notebook_config['dlab_ssh_user'], instance_hostname,
                                                os.environ['conf_key_dir'] + os.environ['conf_key_name'] + ".pem")
        except:
            traceback.print_exc()
            raise Exception
    except Exception as err:
        dlab.fab.append_result("Failed to configure TensorFlow.", str(err))
        AzureActions.remove_instance(notebook_config['resource_group_name'], notebook_config['instance_name'])
        sys.exit(1)

    try:
        print('[INSTALLING USERs KEY]')
        logging.info('[INSTALLING USERs KEY]')
        additional_config = {"user_keyname": notebook_config['user_keyname'],
                             "user_keydir": os.environ['conf_key_dir']}
        params = "--hostname {} --keyfile {} --additional_config '{}' --user {}".format(
            instance_hostname, keyfile_name, json.dumps(additional_config), notebook_config['dlab_ssh_user'])
        try:
            local("~/scripts/{}.py {}".format('install_user_key', params))
        except:
            traceback.print_exc()
            raise Exception
    except Exception as err:
        dlab.fab.append_result("Failed installing users key.", str(err))
        AzureActions.remove_instance(notebook_config['resource_group_name'], notebook_config['instance_name'])
        sys.exit(1)

    try:
        print('[SETUP USER GIT CREDENTIALS]')
        logging.info('[SETUP USER GIT CREDENTIALS]')
        params = '--os_user {} --notebook_ip {} --keyfile "{}"' \
            .format(notebook_config['dlab_ssh_user'], instance_hostname, keyfile_name)
        try:
            local("~/scripts/{}.py {}".format('manage_git_creds', params))
        except:
            dlab.fab.append_result("Failed setup git credentials")
            raise Exception
    except Exception as err:
        dlab.fab.append_result("Failed to setup git credentials.", str(err))
        AzureActions.remove_instance(notebook_config['resource_group_name'], notebook_config['instance_name'])
        sys.exit(1)

    try:
        logging.info('[POST CONFIGURING PROCESS]')
        print('[POST CONFIGURING PROCESS')
        if notebook_config['notebook_image_name'] not in [notebook_config['expected_image_name'], 'None']:
            params = "--hostname {} --keyfile {} --os_user {} --resource_group_name {} --notebook_name {}" \
                .format(instance_hostname, keyfile_name, notebook_config['dlab_ssh_user'],
                        notebook_config['resource_group_name'], notebook_config['instance_name'])
            try:
                local("~/scripts/{}.py {}".format('common_remove_remote_kernels', params))
            except:
                traceback.print_exc()
                raise Exception
    except Exception as err:
        dlab.fab.append_result("Failed to post configuring instance.", str(err))
        AzureActions.remove_instance(notebook_config['resource_group_name'], notebook_config['instance_name'])
        sys.exit(1)

    if notebook_config['image_enabled'] == 'true':
        try:
            print('[CREATING IMAGE]')
            image = AzureMeta.get_image(notebook_config['resource_group_name'],
                                        notebook_config['expected_image_name'])
            if image == '':
                print("Looks like it's first time we configure notebook server. Creating image.")
                dlab.actions_lib.prepare_vm_for_image(True, notebook_config['dlab_ssh_user'], instance_hostname,
                                                      keyfile_name)
                AzureActions.create_image_from_instance(notebook_config['resource_group_name'],
                                                        notebook_config['instance_name'],
                                                        os.environ['azure_region'],
                                                        notebook_config['expected_image_name'],
                                                        json.dumps(notebook_config['image_tags']))
                print("Image was successfully created.")
                local("~/scripts/{}.py".format('common_prepare_notebook'))
                instance_running = False
                while not instance_running:
                    if AzureMeta.get_instance_status(notebook_config['resource_group_name'],
                                                     notebook_config['instance_name']) == 'running':
                        instance_running = True
                instance_hostname = AzureMeta.get_private_ip_address(notebook_config['resource_group_name'],
                                                                     notebook_config['instance_name'])
                dlab.actions_lib.remount_azure_disk(True, notebook_config['dlab_ssh_user'], instance_hostname,
                                                    keyfile_name)
                dlab.fab.set_git_proxy(notebook_config['dlab_ssh_user'], instance_hostname, keyfile_name,
                                       'http://{}:3128'.format(edge_instance_private_hostname))
                additional_config = {"proxy_host": edge_instance_private_hostname, "proxy_port": "3128"}
                params = "--hostname {} --instance_name {} --keyfile {} --additional_config '{}' --os_user {}" \
                    .format(instance_hostname, notebook_config['instance_name'], keyfile_name,
                            json.dumps(additional_config), notebook_config['dlab_ssh_user'])
                local("~/scripts/{}.py {}".format('common_configure_proxy', params))
        except Exception as err:
            dlab.fab.append_result("Failed creating image.", str(err))
            AzureActions.remove_instance(notebook_config['resource_group_name'], notebook_config['instance_name'])
            sys.exit(1)

    try:
        print('[SETUP EDGE REVERSE PROXY TEMPLATE]')
        logging.info('[SETUP EDGE REVERSE PROXY TEMPLATE]')
        additional_info = {
            'instance_hostname': instance_hostname,
            'tensor': True
        }
        params = "--edge_hostname {} " \
                 "--keyfile {} " \
                 "--os_user {} " \
                 "--type {} " \
                 "--exploratory_name {} " \
                 "--additional_info '{}'"\
            .format(edge_instance_private_hostname,
                    keyfile_name,
                    notebook_config['dlab_ssh_user'],
                    'jupyter',
                    notebook_config['exploratory_name'],
                    json.dumps(additional_info))
        try:
            local("~/scripts/{}.py {}".format('common_configure_reverse_proxy', params))
        except:
            dlab.fab.append_result("Failed edge reverse proxy template")
            raise Exception
    except Exception as err:
        dlab.fab.append_result("Failed to set edge reverse proxy template.", str(err))
        AzureActions.remove_instance(notebook_config['resource_group_name'], notebook_config['instance_name'])
        sys.exit(1)

    # generating output information
    try:
        ip_address = AzureMeta.get_private_ip_address(notebook_config['resource_group_name'],
                                                      notebook_config['instance_name'])
        tensorboard_url = "http://" + ip_address + ":6006/"
        jupyter_ip_url = "http://" + ip_address + ":8888/{}/".format(notebook_config['exploratory_name'])
        ungit_ip_url = "http://" + ip_address + ":8085/{}-ungit/".format(notebook_config['exploratory_name'])
        jupyter_notebook_access_url = "https://" + edge_instance_hostname + "/{}/".format(
            notebook_config['exploratory_name'])
        tensorboard_access_url = "https://" + edge_instance_hostname + "/{}-tensor/".format(
            notebook_config['exploratory_name'])
        jupyter_ungit_access_url = "https://" + edge_instance_hostname + "/{}-ungit/".format(
            notebook_config['exploratory_name'])
        print('[SUMMARY]')
        logging.info('[SUMMARY]')
        print("Instance name: {}".format(notebook_config['instance_name']))
        print("Private IP: {}".format(ip_address))
        print("Instance type: {}".format(notebook_config['instance_size']))
        print("Key name: {}".format(notebook_config['key_name']))
        print("User key name: {}".format(notebook_config['user_keyname']))
        print("SG name: {}".format(notebook_config['security_group_name']))
        print("TensorBoard URL: {}".format(tensorboard_url))
        print("TensorBoard log dir: /var/log/tensorboard")
        print("Jupyter URL: {}".format(jupyter_ip_url))
        print("Ungit URL: {}".format(ungit_ip_url))
        print('SSH access (from Edge node, via IP address): ssh -i {0}.pem {1}@{2}'.
              format(notebook_config['key_name'], notebook_config['dlab_ssh_user'], ip_address))

        with open("/root/result.json", 'w') as result:
            res = {"ip": ip_address,
                   "master_keyname": os.environ['conf_key_name'],
                   "tensorboard_log_dir": "/var/log/tensorboard",
                   "notebook_name": notebook_config['instance_name'],
                   "notebook_image_name": notebook_config['notebook_image_name'],
                   "instance_id": notebook_config['instance_name'],
                   "Action": "Create new notebook server",
                   "exploratory_url": [
                       {"description": "Jupyter",
                        "url": jupyter_notebook_access_url},
                       {"description": "TensorBoard",
                        "url": tensorboard_access_url},
                       {"description": "Ungit",
                        "url": jupyter_ungit_access_url}#,
                       #{"description": "Jupyter (via tunnel)",
                       # "url": jupyter_ip_url},
                       #{"description": "TensorBoard (via tunnel)",
                       # "url": tensorboard_url},
                       #{"description": "Ungit (via tunnel)",
                       # "url": ungit_ip_url}
                   ]}
            result.write(json.dumps(res))
    except Exception as err:
        dlab.fab.append_result("Failed to generate output information.", str(err))
        AzureActions.remove_instance(notebook_config['resource_group_name'], notebook_config['instance_name'])
        sys.exit(1)
