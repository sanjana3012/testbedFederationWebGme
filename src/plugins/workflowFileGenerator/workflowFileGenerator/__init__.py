"""
This is where the implementation of the plugin code goes.
The workflowFileGenerator-class is imported from both run_plugin.py and run_debug.py
"""
import sys
import logging
from webgme_bindings import PluginBase
import yaml

# Setup a logger
logger = logging.getLogger('workflowFileGenerator')
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

class workflowFileGenerator(PluginBase):
    def main(self):
        
        logger.info(f"name of active node{self.core.get_attribute(self.active_node,'name')}")
        self.count_of_nodes=0
        self.resource_type_node_initialized = False
        self.resource_type_node = {'node': []}
        self.resource_type_network_initialized = False
        self.resource_type_network = {'network': []}
        self.fabric_networks_with_multiple_nodes=[]
        self.chi_networks_with_multiple_nodes=[]
        self.network_nodes_list=[]
        network_dict={}
        self.nodes = {}
        self.experiment_config={}
        self.fab_file=" "
        

        self.load_nodes()
        

        self.check_experiment_type()
        self.create_provider()

        self.create_fab_file()



        # commit_info = self.util.save(self.root_node, self.commit_hash, 'master', 'Python plugin updated the model')
        # logger.info('committed :{0}'.format(commit_info))
    
    def load_nodes(self):

        nodes_list = self.core.load_sub_tree(self.active_node)        
        for node in nodes_list:
            self.nodes[self.core.get_path(node)] = node
         
        # for n in self.nodes:     
        #     logger.info("Location : {0} : Name of the node : {1}".format(n, self.core.get_attribute(self.nodes[n], "name")))
    
    def create_provider(self):
        self.experiment_config['provider']=[]
        provider_type_chi={} #sub dictionary inside providers
        provider_type_fabric={}
        for path in self.nodes:
            node = self.nodes[path]
            if (self.core.is_instance_of(node, self.META['FabricNode']) or self.core.is_instance_of(node, self.META['FabricNetwork'])):
                if "fabric" not in provider_type_fabric:
                    provider_type_fabric["fabric"]=[]
                    fabric_provider_dict={"fabric_provider":{}}
                    fabric_provider_dict['fabric_provider']["credential_file"]="~/.fabfed/fabfed_credentials.yml"
                    fabric_provider_dict['fabric_provider']["profile"]="fabric"
                    provider_type_fabric["fabric"].append(fabric_provider_dict)
                    self.experiment_config['provider'].append(provider_type_fabric)
                
            
            if (self.core.is_instance_of(node, self.META['ChiNode']) or self.core.is_instance_of(node, self.META['ChiNetwork'])):
                if "chi" not in provider_type_chi: 
                    provider_type_chi["chi"]=[]
                    chi_provider_dict={"chi_provider":{}}
                    chi_provider_dict['chi_provider']["credential_file"]="~/.fabfed/fabfed_credentials.yml"
                    chi_provider_dict['chi_provider']["profile"]="chi"
                    provider_type_chi["chi"].append(chi_provider_dict)
                    self.experiment_config['provider'].append(provider_type_chi)

    def check_has_node_been_processed_before(self,node):

        if node not in self.network_nodes_list:
            self.network_nodes_list.append(node)
            return False
        else:
            return True


    def check_experiment_type(self):

        node_list=[]
        network_list=[]
        stitch_network_connection_list=[]
        simple_network_connection_list=[]
        simple_fabric_connection_list=[]
        simple_chi_connection_list=[]

        for path in self.nodes:
            node = self.nodes[path]
            if (self.core.is_instance_of(node, self.META['Node']) ):
                # logger.info(f"Nodes present in the experiment: {self.core.get_attribute(node, 'name')}")
                node_list.append(node)
                
            if self.core.is_instance_of(node, self.META['Network']):
                # logger.info(f"Networks present in the experiment: {self.core.get_attribute(node, 'name')}")
                network_list.append(node)
            
            if(self.core.is_instance_of(node,self.META['StitchConnection'])):
                # logger.info(f"Stitch Network connections present in the experiment: {self.core.get_attribute(node, 'name')}")
                stitch_network_connection_list.append(node)

            elif(self.core.is_instance_of(node,self.META['SimpleNetworkConnection'])):
                # logger.info(f"Network connections present in the experiment: {self.core.get_attribute(node, 'name')}")
                simple_network_connection_list.append(node)


        if len(simple_network_connection_list)>0:
            if len(stitch_network_connection_list)>0:
                logger.info("full stitch")
                self.full_stitch([node_list,network_list,simple_network_connection_list,stitch_network_connection_list])
                
                
            else:
                logger.info("single provider")
                self.single_provider(node_list,network_list,simple_network_connection_list)
               
                
        elif len(stitch_network_connection_list)>0:
               
            logger.info("HELLOOOOO networks only")
            # self.networks_only([network_list,stitch_network_connection_list])
            
            
                
        else:
            logger.info("simple node")
    
    def create_config(self,network_connection_list):
            self.experiment_config["config"]=[]
            config_type_layer3={}
            connection_dict={}
            for conn in network_connection_list:
                #a dictionary containing a layer3 item (self.config_type_layer3["layer3"])
                # nodes_in_stitch_connection=[]

                
                network_conn_name=self.core.get_attribute(conn,'name')
                if self.core.is_connection(conn):
                    if "layer3" not in config_type_layer3:
                        config_type_layer3["layer3"] =[]
                        if f"{network_conn_name}" not in connection_dict: #a dictionary containing all the attributes and values of a particular connection
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
                        config_type_layer3["layer3"].append(connection_dict)
                        self.experiment_config["config"].append(config_type_layer3)

    
    def finalize_resource_configuration(self):
        # This should be called after all nodes have been processed
        if 'resource' not in self.experiment_config:
            self.experiment_config['resource'] = []
        self.experiment_config['resource'].append(self.resource_type_node)
        self.experiment_config['resource'].append(self.resource_type_network)
        # Reset for potential future use
        self.resource_type_node = {'node': []}
        self.resource_type_node_initialized = False       
    
    def process_node(self,node,len_node_list=0,stitch="no"):
    
        if not self.core.get_pointer_path(node,'credential_file'):
            raise Exception(f"Credential file not attached to {self.core.get_attribute(node,'name')}")
        else:
            logger.info(f"NAME OF NODE AGHHH {self.core.get_attribute(node,'name')}")
            self.count_of_nodes+=1
            logger.info(f"COUNT OF NODES {self.count_of_nodes} AND NODE LIST LENGTH {len_node_list}")
            if not self.resource_type_node_initialized:
                self.resource_type_node_initialized = True
            node_attributes = self.core.get_attribute_names(node)
            logger.info(f"node attribute names are: {node_attributes}")
            node_dict={}
            node_name=self.core.get_attribute(node,"name")
            
            if f"{node_name}" not in node_dict: #a dictionary storing all attributes and values of a node (self.resource_type_node["node"]["node_dict"]["node_name"])
                node_dict[f"{node_name}"] ={}
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
                elif attribute_name=="nic_model":
                    node_nic_model= self.core.get_attribute(node,attribute_name)
                    node_dict[f"{node_name}"]["nic_model"]=node_nic_model

                elif attribute_name=="network":
                    if stitch=="yes":
                        node_dict[f"{node_name}"]["network"]="'{{ network.chi_network }}'"
                    else:
                        node_network=self.core.get_attribute(node,attribute_name)
                        node_dict[f"{node_name}"]["network"]=node_network          
            
            if self.core.is_instance_of(node, self.META['FabricNode']):
                node_dict[f"{node_name}"]['provider'] = "'{{fabric.fabric_provider}}'"
            
            if self.core.is_instance_of(node, self.META['ChiNode']):
                node_dict[f"{node_name}"]['provider'] = "'{{chi.chi_provider}}'"

            self.resource_type_node['node'].append(node_dict)
            # if self.count_of_nodes==1:
            #     self.finalize_resource_configuration()
    
    

    
    def process_network(self,node,interface,network_conn_name,interface_required="yes",stitch="no"):
        network_dict={}
        if interface_required == "no" and not self.core.get_pointer_path(node, 'credential_file'):
            raise Exception(f"Credential file not attached to {self.core.get_attribute(node, 'name')}")
        
        if not self.resource_type_network_initialized:
                self.resource_type_network_initialized = True
        
        logger.info(f"HELOOOOOO INTERFACE {interface}")
        if self.core.is_instance_of(node, self.META['FabricNetwork']):
            node_attributes = self.core.get_attribute_names(node)
            if 'fabric_network' not in network_dict:
                network_dict['fabric_network']={}
                network_dict['fabric_network']['provider']="'{{fabric.fabric_provider}}'"
                network_dict['fabric_network']['layer3']=f"{{{{ layer3.{network_conn_name} }}}}"
                network_dict['fabric_network']['interface']=interface
                if stitch=="yes":
                    network_dict['fabric_network']['stitch_with']= '{{ network.chi_network }}'
        
        if self.core.is_instance_of(node,self.META['ChiNetwork']):
                        
            if 'chi_network' not in network_dict: #a dictionary containing all the attributes and values of the fabric network
            
                network_dict['chi_network']={}
                network_dict['chi_network']['provider']="'{{chi.chi_provider}}'"
                network_dict['chi_network']['layer3']=f"{{{{ layer3.{network_conn_name} }}}}"
                site=self.core.get_attribute(node,"site")
                network_dict['chi_network']['site']=f"{site}"
              
        self.resource_type_network['network'].append(network_dict)
        


            
        
    def process_simple_network_connection(self,network_conn_name,simple_network_connection_list,len_node_list=0,stitch="no"):

        
        
        interface_required="yes"
        interface=[]

        if stitch=="no":
            self.create_config(simple_network_connection_list)
        

        for conn in simple_network_connection_list:
            nodes_in_simple_connection=[]
            if stitch=="no":
                network_conn_name=self.core.get_attribute(conn,'name')
            logger.info(f"NAME OF CONN AGHHH {self.core.get_attribute(conn,'name')}")
            source_node=self.nodes[self.core.get_pointer_path(conn,'src')]
            logger.info(f"Source node is {self.core.get_attribute(source_node,'name')}")

            source_node_name=self.core.get_attribute(source_node,"name")
            nodes_in_simple_connection.append(source_node)

            
            destination_node=self.nodes[self.core.get_pointer_path(conn,'dst')]
            logger.info(f"Destination node is {self.core.get_attribute(destination_node,'name')}")
        

            destination_node_name=self.core.get_attribute(destination_node,"name")
            nodes_in_simple_connection.append(destination_node)

            if self.core.is_instance_of(source_node, self.META['Network']) and self.core.is_instance_of(destination_node,self.META['Node']):

                for node in nodes_in_simple_connection:
                    if self.core.is_instance_of(node, self.META['Node']):

                        logger.info(f"NAME OF NODE INSIDE THE PROCESS SIMPLE FUNCTIONAGHHH {self.core.get_attribute(node,'name')}")
                        
                        if self.core.is_instance_of(node, self.META['FabricNode']):
                             
                            node_name=self.core.get_attribute(node,"name")
                            interface.append(f"{{{{ node.{node_name} }}}}")
                        self.process_node(node,len_node_list,stitch)
                
        for conn in simple_network_connection_list:
            nodes_in_simple_connection=[]
            if stitch=="no":
                network_conn_name=self.core.get_attribute(conn,'name')
            logger.info(f"NAME OF CONN AGHHH {self.core.get_attribute(conn,'name')}")
            source_node=self.nodes[self.core.get_pointer_path(conn,'src')]
            logger.info(f"Source node is {self.core.get_attribute(source_node,'name')}")

            source_node_name=self.core.get_attribute(source_node,"name")
            nodes_in_simple_connection.append(source_node)

            
            destination_node=self.nodes[self.core.get_pointer_path(conn,'dst')]
            logger.info(f"Destination node is {self.core.get_attribute(destination_node,'name')}")
        

            destination_node_name=self.core.get_attribute(destination_node,"name")
            nodes_in_simple_connection.append(destination_node)

            if self.core.is_instance_of(source_node, self.META['Network']) and self.core.is_instance_of(destination_node,self.META['Node']):


                for node in nodes_in_simple_connection:
                
                    if self.core.is_instance_of(node, self.META['Network']):
                        
                        if not self.check_has_node_been_processed_before(node):
                            logger.info(f"UNIQUE NETWORK IN TOPO {self.core.get_attribute(node,'name')}")
                            self.process_network(node,InlineList(interface),network_conn_name,interface_required,stitch)
        



    def process_stitch_connection(self,stitch_network_connection_list):

        nodes_in_stitch_connection=[]

        for conn in stitch_network_connection_list:

            source_node=self.nodes[self.core.get_pointer_path(conn,'src')]
            logger.info(f"Source node is {self.core.get_attribute(source_node,'name')}")

            source_node_name=self.core.get_attribute(source_node,"name")
            nodes_in_stitch_connection.append(source_node)

            
            destination_node=self.nodes[self.core.get_pointer_path(conn,'dst')]
            logger.info(f"Destination node is {self.core.get_attribute(destination_node,'name')}")
        

            destination_node_name=self.core.get_attribute(destination_node,"name")
            nodes_in_stitch_connection.append(destination_node)
    
        
            
        
    def full_stitch(self,concepts):

        node_list,network_list,simple_network_connection_list,stitch_network_connection_list=concepts
        for conn in stitch_network_connection_list:
            network_conn_name=self.core.get_attribute(conn,"name")
        self.create_config(stitch_network_connection_list)
        self.process_simple_network_connection(network_conn_name,simple_network_connection_list,len(node_list),stitch="yes")
        self.finalize_resource_configuration()

    def single_provider(self,concepts):
        node_list,network_list,simple_network_connection_list=concepts
        for conn in simple_network_connection_list:
            network_conn_name=self.core.get_attribute(conn,"name")
        self.process_simple_network_connection(network_conn_name,simple_network_connection_list,len(node_list),stitch="no")
        self.finalize_resource_configuration()

        
    


    


    def create_fab_file(self):
        yaml_string = yaml.dump(self.experiment_config, default_flow_style=False)
        self.fab_file=yaml_string.replace("'''","'")
        self.add_file("fabric_config.fab", self.fab_file)           
        commit_info = self.util.save(self.root_node, self.commit_hash, 'master', 'Python plugin updated the model')
        logger.info('committed :{0}'.format(commit_info))

   

            
        
            
    



