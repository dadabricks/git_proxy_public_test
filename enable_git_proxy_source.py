# Databricks notebook source
# MAGIC %md
# MAGIC # Enable Git Proxy for private Git server connectivity in Repos

# COMMAND ----------

# MAGIC %md
# MAGIC ### Overview
# MAGIC This private preview feature is available on AWS and Azure.
# MAGIC
# MAGIC **Note**: an *admin* must run this notebook to enable the feature.
# MAGIC
# MAGIC "Run all" this notebook to set up a cluster that proxies requests to your private Git server. Running this notebook does the following things:
# MAGIC
# MAGIC 0. Writes a shell script to DBFS (`dbfs:/databricks/db_repos_proxy/db_repos_proxy_init.sh`) that is used as a [cluster-scoped init script](https://docs.databricks.com/clusters/init-scripts.html#example-cluster-scoped-init-scripts).
# MAGIC 0. Creates a [single node cluster](https://docs.databricks.com/clusters/single-node.html) named `dp_git_proxy` that runs the init script on start-up. **Important**: all users in the workspace will be granted "attach to" permissions to the cluster.
# MAGIC 0. Enables a feature flag that controls whether Git requests in Repos are proxied via the cluster.
# MAGIC
# MAGIC You may need to wait several minutes after running this notebook for the cluster to reach a "RUNNING" state. It can also take up to 30 minutes for the feature flag configuration to take effect.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Write Cluster Init Script to DBFS

# COMMAND ----------

db_repos_proxy_init = """
#!/bin/bash
set -x

#--------------------------------------------------
# Install Python
mkdir /databricks/db_repos_proxy
/databricks/python3/bin/python -m pip install --upgrade pip
python3 -m pip install https://github.com/dadabricks/git_proxy_public_test/archive/refs/tags/v0.0.18.zip

#--------------------------------------------------
# Setup Systemd
cat > /etc/systemd/system/db_repos_proxy.service <<EOF
[Service]
Type=simple
Environment=ENABLE_SSL_VERIFICATION=true CA_CERT_PATH=''
ExecStart=/databricks/python3/bin/db_proxy
StandardInput=null
StandardOutput=file:/databricks/db_repos_proxy/daemon.log
StandardError=file:/databricks/db_repos_proxy/daemon.log
Restart=always
RestartSec=1

[Unit]
Description=Git Proxy Service

[Install]
WantedBy=multi-user.target
EOF
#--------------------------------------------------

systemctl daemon-reload
systemctl enable db_repos_proxy.service
systemctl start db_repos_proxy.service
"""  # db_repos_proxy_init_end

location = "/databricks/db_repos_proxy/db_repos_proxy_init.sh"
dbutils.fs.mkdirs("dbfs:/databricks/db_repos_proxy/")
dbutils.fs.put(location, db_repos_proxy_init, True)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create the proxy cluster

# COMMAND ----------

dbutils.widgets.text("cluster-name", "", "Git Proxy Cluster Name")

# COMMAND ----------

import requests

admin_token = (
    dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()
)
databricks_instance = (
    dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiUrl().get()
)

headers = {"Authorization": f"Bearer {admin_token}"}

# Clusters
CLUSTERS_LIST_ENDPOINT = "/api/2.0/clusters/list"
CLUSTERS_CREATE_ENDPOINT = "/api/2.0/clusters/create"
CLUSTERS_LIST_NODE_TYPES_ENDPOINT = "/api/2.0/clusters/list-node-types"

# Permissions
UPDATE_PERMISSIONS_ENDPOINT = "/api/2.0/permissions/clusters"

# Workspace Conf
WORKSPACE_CONF_ENDPOINT = "/api/2.0/workspace-conf"

# get name to use for cluster
cluster_name = "dp_git_proxy"  # default name
widget_value = dbutils.widgets.get("cluster-name")
workspace_conf_value = requests.get(
    databricks_instance + WORKSPACE_CONF_ENDPOINT + "?keys=gitProxyClusterName",
    headers=headers,
).json()["gitProxyClusterName"]
print(f"widget value: {widget_value}")
print(f"workspace conf value: {workspace_conf_value}")

if widget_value:
    cluster_name = widget_value
elif workspace_conf_value:
    cluster_name = workspace_conf_value
print(f"Using cluster name {cluster_name}")

# COMMAND ----------

create_cluster_data = {
    "cluster_name": cluster_name,
    "spark_version": "12.2.x-scala2.12",
    "num_workers": 0,
    "autotermination_minutes": 0,
    "spark_conf": {
        "spark.databricks.cluster.profile": "singleNode",
        "spark.master": "local[*]",
    },
    "custom_tags": {"ResourceClass": "SingleNode"},
    "init_scripts": {
        "dbfs": {
            "destination": "dbfs:/databricks/db_repos_proxy/db_repos_proxy_init.sh"
        }
    },
}
# get list of node types to determine whether this workspace is on AWS or Azure
clusters_node_types = requests.get(
    databricks_instance + CLUSTERS_LIST_NODE_TYPES_ENDPOINT, headers=headers
).json()["node_types"]
node_type_ids = [type["node_type_id"] for type in clusters_node_types]
aws_node_type_id = "m5.large"
azure_node_type_id = "Standard_DS3_v2"
if aws_node_type_id in node_type_ids:
    create_cluster_data = {
        **create_cluster_data,
        "node_type_id": aws_node_type_id,
        "aws_attributes": {"ebs_volume_count": "1", "ebs_volume_size": "32"},
    }
elif azure_node_type_id in node_type_ids:
    create_cluster_data = {**create_cluster_data, "node_type_id": azure_node_type_id}
else:
    raise ValueError(
        f"Node types {aws_node_type_id} or {azure_node_type_id} do not exist. Make sure you are on AWS or Azure, or contact support."
    )

# Note: this only returns up to 100 terminated all-purpose clusters in the past 30 days
clusters_list_response = requests.get(
    databricks_instance + CLUSTERS_LIST_ENDPOINT, headers=headers
).json()
clusters_list = clusters_list_response["clusters"]
clusters_names = [
    cluster["cluster_name"] for cluster in clusters_list_response["clusters"]
]
print(f"List of existing clusters: {clusters_names}")

if cluster_name in clusters_names:
    raise ValueError(
        f"Cluster called {cluster_name} already exists. Please delete this cluster and re-run this notebook"
    )
else:
    # Create a new cluster named cluster_name that will proxy requests to the private Git server
    print(f"Create cluster POST request data: {create_cluster_data}")
    clusters_create_response = requests.post(
        databricks_instance + CLUSTERS_CREATE_ENDPOINT,
        headers=headers,
        json=create_cluster_data,
    ).json()
    print(f"Create cluster response: {clusters_create_response}")
    cluster_id = clusters_create_response["cluster_id"]
    print(f"Created new cluster with id {cluster_id}")
    update_permissions_data = {
        "access_control_list": [
            {"group_name": "users", "permission_level": "CAN_ATTACH_TO"}
        ]
    }
    update_permissions_response = requests.patch(
        databricks_instance + UPDATE_PERMISSIONS_ENDPOINT + f"/{cluster_id}",
        headers=headers,
        json=update_permissions_data,
    ).json()
    print(f"Update permissions response: {update_permissions_response}")
    print(f"Gave all users ATTACH TO permissions to cluster {cluster_id}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Flip the feature flag!
# MAGIC This flips the feature flag to route Git requests to the cluster. The change should take into effect within an hour.

# COMMAND ----------

patch_enable_git_proxy_data = {"enableGitProxy": "true"}
patch_git_proxy_cluster_name_data = {"gitProxyClusterName": cluster_name}
requests.patch(
    databricks_instance + WORKSPACE_CONF_ENDPOINT,
    headers=headers,
    json=patch_enable_git_proxy_data,
)
requests.patch(
    databricks_instance + WORKSPACE_CONF_ENDPOINT,
    headers=headers,
    json=patch_git_proxy_cluster_name_data,
)

# COMMAND ----------

# MAGIC %md
# MAGIC #### Check that flag has been set
# MAGIC If the command below returns with `{"enableGitProxy":"true"}`, you should be all set. Also, if you configured a custom cluster name using the widget, check that the cluster name in the response matches the name you specified.

# COMMAND ----------

get_flag_response = requests.get(
    databricks_instance + WORKSPACE_CONF_ENDPOINT + "?keys=enableGitProxy",
    headers=headers,
).json()
get_cluster_name_response = requests.get(
    databricks_instance + WORKSPACE_CONF_ENDPOINT + "?keys=gitProxyClusterName",
    headers=headers,
).json()
print(f"Get enableGitProxy response: {get_flag_response}")
print(f"Get gitProxyClusterName response: {get_cluster_name_response}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Validation steps
# MAGIC Attach this notebook to the **Git proxy cluster** that was just created and follow the instructions below.

# COMMAND ----------

# MAGIC %sh
# MAGIC systemctl status db_repos_proxy.service
# MAGIC journalctl -u db_repos_proxy.service
# MAGIC cat /databricks/db_repos_proxy/daemon.log

# COMMAND ----------

# MAGIC %sh
# MAGIC /databricks/python3/bin/db_proxy_doctor

# COMMAND ----------

# MAGIC %sh
# MAGIC python --version

# COMMAND ----------

# MAGIC %sh
# MAGIC curl localhost:8000/databricks/health

# COMMAND ----------
