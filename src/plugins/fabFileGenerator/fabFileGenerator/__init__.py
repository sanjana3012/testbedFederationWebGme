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
        self.provider={
        '-fabric': {
        '-fabric_provider': {
            'credential_file': '~/.fabfed/fabfed_credentials.yml',
            'profile': 'fabric'
        }
    }
}
        self.resource={}
        self.variable_list=[]
        self.provider_list=[]
        self.resource_list=[]
        self.fab_file=""
        
        # hello

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
                logger.info(self.core.get_attribute(node, "name"))
                self.resource_list.append(node)

        for node in self.resource_list:

            
            if self.core.is_instance_of(node, self.META['FabricNode']):
                if not self.core.get_pointer_path(node,'credential_file'):
                    raise Exception("failed")
                else:

                    c_path=self.core.get_pointer_path(node,'credential_file')
                    if "fabric" not in self.provider_list: 
                        self.provider_list.append("fabric")

                    fabric_node_attributes = self.core.get_attribute_names(node)
                    logger.info(f"fabric node attribute names are: {fabric_node_attributes}")

                    for attribute_name in fabric_node_attributes:
#                   
                        if attribute_name=="name":
                            node_name=self.core.get_attribute(node,attribute_name)
                        elif attribute_name=="count":
                            node_count=self.core.get_attribute(node,attribute_name)
                        elif attribute_name=="site":
                            node_site=self.core.get_attribute(node,attribute_name)
                        elif attribute_name=="nic_model":
                            node_nic_model=self.core.get_attribute(node,attribute_name)
                        elif attribute_name=="image":
                            node_image=self.core.get_attribute(node,attribute_name)
                    
                    self.variable={'-fabric_site':{'default':f"{node_site}"},
                                '-node_name':{'default':f"{node_name}"}}
                    if '-node' not in self.resource:
                        self.resource['-node'] = {}

        
                    if f"{node_name}" not in self.resource['-node']:
                        self.resource['-node'][f"{node_name}"] = {}

                
                    self.resource['-node'][f"{node_name}"]['provider'] = '{{ fabric.fabric_provider }}'
                    self.resource['-node'][f"{node_name}"]['site'] = '{{ var.fabric_site }}'
                    self.resource['-node'][f"{node_name}"]['count'] = node_count
                    self.resource['-node'][f"{node_name}"]['image'] = node_image
                    self.resource['-node'][f"{node_name}"]['nic_model'] = node_nic_model
                    
            
        
        
                    experiment_config = {
                'variable': self.variable,
                'provider': self.provider,
                'resource': self.resource
            }
                    self.fab_file = yaml.dump(experiment_config, default_flow_style=False)
                
                


                    self.add_file("fabric_config.fab", self.fab_file)

#                 
        commit_info = self.util.save(self.root_node, self.commit_hash, 'master', 'Python plugin updated the model')
        logger.info('committed :{0}'.format(commit_info))
               
                        
                        
                        

                          
        
        
     
