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


class fabFileGenerator(PluginBase):
    def main(self):
        self.nodes = {}
        self.variable={}
        self.provider={}
        self.resource={}
        self.config={'-layer3':{}}
        self.variable_list=[]
        self.node_list=[]
        self.network_list=[]
        self.network_connection=[]
        self.provider_list=[]
        self.resource_list=[]
        # Initializing a dictionary with keys and a None value for each
        keys = ['provider', 'resource']
        self.experiment_config={key: {} for key in keys}
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
                self.node_list.append(node)

            if (self.core.is_instance_of(node, self.META['FabricNetwork']) or self.core.is_instance_of(node, self.META['ChiNetwork'])):
                logger.info(f"Networks present in the experiment: {self.core.get_attribute(node, 'name')}")
                self.network_list.append(node)
            
            if(self.core.is_instance_of(node,self.META['NetworkConnection'])):
                logger.info(f"Network connections present in the experiment: {self.core.get_attribute(node, 'name')}")
                self.network_connection.append(node)

        for node in self.node_list:

                if self.core.is_instance_of(node, self.META['FabricNode']) or self.core.is_instance_of(node, self.META['ChiNode']):
                    if not self.core.get_pointer_path(node,'credential_file'):
                        raise Exception(f"Credential file not attached to {self.core.get_attribute(node,'name')}")
                    else:

                        c_path=self.core.get_pointer_path(node,'credential_file')
                        c_name=self.core.get_attribute(node,'name')
                    

                        node_attributes = self.core.get_attribute_names(node)
                        #logger.info(f"node attribute names are: {node_attributes}")

                        for attribute_name in node_attributes:
    #                   
                            if attribute_name=="name":
                                node_name=self.core.get_attribute(node,attribute_name)
                            elif attribute_name=="count":
                                node_count=self.core.get_attribute(node,attribute_name)
                            elif attribute_name=="site":
                                node_site=self.core.get_attribute(node,attribute_name)
                            elif attribute_name=="image":
                                node_image=self.core.get_attribute(node,attribute_name)
                        
                        # self.variable={'-fabric_site':{'default':f"{node_site}"},
                        #             '-node_name':{'default':f"{node_name}"}}
                        if '-node' not in self.resource:
                            self.resource['-node'] = {}

            
                        if f"{node_name}" not in self.resource['-node']:
                            self.resource['-node'][f"{node_name}"] = {}

                        self.resource['-node'][f"{node_name}"]['site'] = node_site
                        self.resource['-node'][f"{node_name}"]['count'] = node_count
                        self.resource['-node'][f"{node_name}"]['image'] = node_image

                        if self.core.is_instance_of(node, self.META['FabricNode']):
                            if "fabric" not in self.provider_list: 
                                self.provider_list.append("fabric")
                                self.provider['-fabric']={}
                                self.provider['-fabric']['-fabric_provider']={}
                                self.provider['-fabric']['-fabric_provider']['credential_file']= "~/.fabfed/fabfed_credentials.yml"
                                self.provider['-fabric']['-fabric_provider']['profile']="fabric"
                            self.resource['-node'][f"{node_name}"]['provider'] = '{{ fabric.fabric_provider }}'

                        elif self.core.is_instance_of(node, self.META['ChiNode']):
                            if "chi" not in self.provider_list: 
                                self.provider_list.append("chi")
                                self.provider['-chi']={}
                                self.provider['-chi']['-chi_provider']={}
                                self.provider['-chi']['-chi_provider']['credential_file']= "~/.fabfed/fabfed_credentials.yml"
                                self.provider['-chi']['-chi_provider']['profile']="chi"
                            self.resource['-node'][f"{node_name}"]['provider'] = '{{ chi.chi_provider }}'     
                        
                        self.experiment_config['provider']=self.provider
                        self.experiment_config['resource']=self.resource


                        
        for node in self.network_connection:
            nodes_in_connection=[]
            interface=[]
            network_conn_name=self.core.get_attribute(node,'name')
            if self.core.is_connection(node):
                logger.info(f"Network Connection is: {self.core.get_attribute(node,'name')}")
                source_node=self.nodes[self.core.get_pointer_path(node,'src')]
                source_node_name=self.core.get_attribute(source_node,"name")
                nodes_in_connection.append(source_node)

                logger.info(f"Source node is {self.core.get_attribute(source_node,'name')}")
                destination_node=self.nodes[self.core.get_pointer_path(node,'dst')]
                destination_node_name=self.core.get_attribute(destination_node,"name")
                nodes_in_connection.append(destination_node)
                logger.info(f"Destination node is {self.core.get_attribute(destination_node,'name')}")

                for node_x in nodes_in_connection:
                    if self.core.is_instance_of(node_x,self.META['FabricNode']):
                        node_name1=self.core.get_attribute(node_x,"name")
                        interface.append(f"{{{{ node.{node_name1} }}}}")
                        if '-network' not in self.resource:
                            self.resource['-network'] = {}
                        if '-fabric_network' not in self.resource:
                            self.resource['-network']['-fabric_network'] = {}

                        self.resource['-network']['-fabric_network']['provider']='{{ fabric.fabric_provider }}'

                        
                self.resource['-network']['-fabric_network']['interface']= interface #have to figure out
                self.resource['-network']['-fabric_network']['layer3']=f"{{{{ layer3.{network_conn_name} }}}}"
                    



                node_attributes = self.core.get_attribute_names(node)
                        #logger.info(f"node attribute names are: {node_attributes}")
                for attribute_name in node_attributes:
                    if attribute_name=="subnet":
                        network_subnet=self.core.get_attribute(node,attribute_name)
                    elif attribute_name=="gateway":
                        network_gateway= self.core.get_attribute(node,attribute_name)
                    elif attribute_name=="ip_start":
                        network_ip_start=self.core.get_attribute(node,attribute_name)
                    elif attribute_name=="ip_end":
                        network_ip_end=self.core.get_attribute(node,attribute_name)

                self.config['-layer3'][f"-{network_conn_name}"]={}
                self.config['-layer3'][f'-{network_conn_name}']['subnet']= network_subnet
                self.config['-layer3'][f'-{network_conn_name}']['gateway']= network_gateway
                self.config['-layer3'][f'-{network_conn_name}']['ip_start']= network_ip_start
                self.config['-layer3'][f'-{network_conn_name}']['ip_end']= network_ip_end

                self.experiment_config['config']={}
                self.experiment_config['config']=self.config


            
        self.fab_file = yaml.dump(self.experiment_config, default_flow_style=False)
        self.add_file("fabric_config.fab", self.fab_file)           
        commit_info = self.util.save(self.root_node, self.commit_hash, 'master', 'Python plugin updated the model')
        logger.info('committed :{0}'.format(commit_info))
               
                        
                        
                        

                          
        
        
     
