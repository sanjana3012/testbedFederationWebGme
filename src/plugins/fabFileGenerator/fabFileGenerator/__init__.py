"""
This is where the implementation of the plugin code goes.
The fabFileGenerator-class is imported from both run_plugin.py and run_debug.py
"""
import sys
import logging
import yaml
from webgme_bindings import PluginBase

# Setup a logger
logger = logging.getLogger('fabFileGenerator')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)  # By default it logs to stderr..
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class InlineList(list):
    """A subclass of list to represent specific lists inline in YAML."""
    pass

def represent_inline_list(dumper, data):
    """Tell PyYAML to represent instances of InlineList using flow style (inline)."""
    return dumper.represent_sequence(u'tag:yaml.org,2002:seq', data, flow_style=True)

# Register the InlineList representer with PyYAML
yaml.add_representer(InlineList, represent_inline_list)

class fabFileGenerator(PluginBase):
    def main(self):
        self.nodes = {}
        self.variable={} #not using it
        self.provider=[] #main list for providers
        self.resource=[] #main list for resources
        self.config=[]
        self.provider_type_chi={} #sub dictionary inside providers
        self.provider_type_fabric={}
        self.resource_type_node={} #sub dictionary inside resources
        self.resource_type_network={}
        self.config_dict={}
        
        self.variable_list=[] #not using
        self.node_list=[] #using to keep track of nodes
        self.network_list=[] #using to keep track of networks
        self.network_connection=[] #using to keep track of network connections
        self.provider_list=[] #not really using
        self.resource_list=[] #not really using
        self.node_list_names=[] #not really using
        self.credential_list=[] #not really using
        
        #main dictionary for the experiment
        keys = ['provider', 'resource','config']
        self.experiment_config={key: [] for key in keys}

        #file for the experiment
        self.fab_file=""

        nodes_list = self.core.load_sub_tree(self.active_node)        
        for node in nodes_list:
            self.nodes[self.core.get_path(node)] = node
        
        # for n in self.nodes:     
        #     logger.info("Location : {0} : Name of the node : {1}".format(n, self.core.get_attribute(self.nodes[n], "name")))
            
        self.fetch_fab_file()

    def fetch_fab_file(self):
        
        for path in self.nodes:
            node = self.nodes[path]
            if (self.core.is_instance_of(node, self.META['FabricNode']) or self.core.is_instance_of(node, self.META['ChiNode'])):
                logger.info(f"Nodes present in the experiment: {self.core.get_attribute(node, 'name')}")
                if "node" not in self.resource_type_node:
                    self.resource_type_node["node"]=[]
                self.node_list.append(node)
                

            if (self.core.is_instance_of(node, self.META['FabricNetwork']) or self.core.is_instance_of(node, self.META['ChiNetwork'])):
                logger.info(f"Networks present in the experiment: {self.core.get_attribute(node, 'name')}")
                
                self.network_list.append(node)
            
            if(self.core.is_instance_of(node,self.META['NetworkConnection'])):
                logger.info(f"Network connections present in the experiment: {self.core.get_attribute(node, 'name')}")
                if "network" not in self.resource_type_network:
                    self.resource_type_network["network"]=[]
                if "layer3" not in self.config_dict:
                    self.config_dict["layer3"]=[]

                self.network_connection.append(node)

        for node in self.node_list:
                node_dict={}

                if self.core.is_instance_of(node, self.META['FabricNode']) or self.core.is_instance_of(node, self.META['ChiNode']):
                    if not self.core.get_pointer_path(node,'credential_file'):
                        raise Exception(f"Credential file not attached to {self.core.get_attribute(node,'name')}")
                    else:
                        
                        
                        c_path=self.core.get_pointer_path(node,'credential_file')
                        c_name=self.core.get_attribute(node,'name')
                    

                        node_attributes = self.core.get_attribute_names(node)
                        #logger.info(f"node attribute names are: {node_attributes}")
                        node_name=self.core.get_attribute(node,"name")
                        node_dict={}
                        if f"{node_name}" not in node_dict:
                            node_dict[f"{node_name}"] ={}
                        fab_dict={}
                        # provider_dict={}

                        for attribute_name in node_attributes:

                            if attribute_name=="count":
                                node_count=self.core.get_attribute(node,attribute_name)
                                node_dict[f"{node_name}"]["count"]=node_count
                            elif attribute_name=="site":
                                node_site=self.core.get_attribute(node,attribute_name)
                                node_dict[f"{node_name}"]["site"]=node_site
                            elif attribute_name=="image":
                                node_image=self.core.get_attribute(node,attribute_name)
                                node_dict[f"{node_name}"]["image"]=node_image                       
                      
                        if self.core.is_instance_of(node, self.META['FabricNode']):
                            if "fabric" not in self.provider_type_fabric: 
                                self.provider_type_fabric["fabric"]=[]
                                fabric_provider_dict={"fabric_provider":{}}
                                fabric_provider_dict['fabric_provider']["credential_file"]="~/.fabfed/fabfed_credentials.yml"
                                fabric_provider_dict['fabric_provider']["profile"]="fabric"
                                self.provider_type_fabric["fabric"].append(fabric_provider_dict)
                            node_dict[f"{node_name}"]['provider'] = "'{{fabric.fabric_provider}}'"
                        
                        if self.core.is_instance_of(node, self.META['ChiNode']):
                            if "chi" not in self.provider_type_chi: 
                                self.provider_type_chi["chi"]=[]
                                fabric_provider_dict={"chi_provider":{}}
                                fabric_provider_dict['chi_provider']["credential_file"]="~/.fabfed/fabfed_credentials.yml"
                                fabric_provider_dict['chi_provider']["profile"]="chi"
                                self.provider_type_chi["chi"].append(fabric_provider_dict)
                            node_dict[f"{node_name}"]['provider'] = "'{{chi.chi_provider}}'"
                self.resource_type_node['node'].append(node_dict)
 


                
                                    
                       
        
        # print(self.experiment_config)
                        
        for conn in self.network_connection:
            network_dict={}
            connection_dict={}

            nodes_in_connection=[]
            interface=[]
            network_conn_name=self.core.get_attribute(conn,'name')
            if self.core.is_connection(conn):
                if "layer3" in self.config_dict and self.config_dict["layer3"] == []:
                    if f"{network_conn_name}" not in connection_dict:
                        connection_dict[f"{network_conn_name}"]={}
                        conn_attributes = self.core.get_attribute_names(conn)
                    for attribute_name in conn_attributes:
                        if attribute_name=="subnet":
                            network_subnet=self.core.get_attribute(conn,attribute_name)
                            connection_dict[f"{network_conn_name}"]["subnet"]=network_subnet
                        elif attribute_name=="gateway":
                            network_gateway= self.core.get_attribute(conn,attribute_name)
                            connection_dict[f"{network_conn_name}"]["gateway"]=network_gateway
                        elif attribute_name=="ip_start":
                            network_ip_start=self.core.get_attribute(conn,attribute_name)
                            connection_dict[f"{network_conn_name}"]["ip_start"]=network_ip_start
                        elif attribute_name=="ip_end":
                            network_ip_end=self.core.get_attribute(conn,attribute_name)
                            connection_dict[f"{network_conn_name}"]["ip_end"]=network_ip_end
                    self.config_dict["layer3"].append(connection_dict)
                
                    logger.info(f"Network Connection is: {self.core.get_attribute(conn,'name')}")
                    source_node=self.nodes[self.core.get_pointer_path(conn,'src')]
                    source_node_name=self.core.get_attribute(source_node,"name")
                    nodes_in_connection.append(source_node)

                    logger.info(f"Source node is {self.core.get_attribute(source_node,'name')}")
                    destination_node=self.nodes[self.core.get_pointer_path(conn,'dst')]
                    destination_node_name=self.core.get_attribute(destination_node,"name")
                    nodes_in_connection.append(destination_node)
                    logger.info(f"Destination node is {self.core.get_attribute(destination_node,'name')}")


                    for node in nodes_in_connection:
                        if self.core.is_instance_of(node,self.META['FabricNode']):
                            node_name=self.core.get_attribute(node,"name")
                            interface.append(f"{{{{ node.{node_name} }}}}")
                            if 'fabric_network' not in network_dict:
                            
                                network_dict['fabric_network']={}
                                network_dict['fabric_network']['provider']="'{{fabric.fabric_provider}}'"
                                network_dict['fabric_network']['layer3']=f"{{{{ layer3.{network_conn_name} }}}}"
                                network_dict['fabric_network']['interface']=interface
                    
                            if network_dict['fabric_network']['interface']:
                                network_dict['fabric_network']['interface']=InlineList(interface)

                self.resource_type_network["network"].append(network_dict)
            



        self.experiment_config['provider']=[self.provider_type_fabric,self.provider_type_chi]
        self.experiment_config['resource']=[self.resource_type_node]
        # self.experiment_config['config']=[self.config_dict]

        logger.info(self.experiment_config)

        yaml_string = yaml.dump(self.experiment_config, default_flow_style=False)
        self.fab_file=yaml_string.replace("'''","'")
        self.add_file("fabric_config.fab", self.fab_file)           
        commit_info = self.util.save(self.root_node, self.commit_hash, 'master', 'Python plugin updated the model')
        logger.info('committed :{0}'.format(commit_info))
               
                        
                        
                        

                          
        
        
     
