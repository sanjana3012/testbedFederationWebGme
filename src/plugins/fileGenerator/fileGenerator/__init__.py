"""
This is where the implementation of the plugin code goes.
The fileGenerator-class is imported from both run_plugin.py and run_debug.py
"""
import sys
import logging
from webgme_bindings import PluginBase

# Setup a logger
logger = logging.getLogger('fileGenerator')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)  # By default it logs to stderr..
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class fileGenerator(PluginBase):
    def main(self):      
        self.nodes = {}
        self.credentials = []
        self.credential_file = ""
        # hello

        nodes_list = self.core.load_sub_tree(self.active_node)        
        for node in nodes_list:
            self.nodes[self.core.get_path(node)] = node
        
        # for n in self.nodes:     
        #     logger.info("Location : {0} : Name of the node : {1}".format(n, self.core.get_attribute(self.nodes[n], "name")))
            
        self.fetch_credentials()

    def fetch_credentials(self):
        for path in self.nodes:
            node = self.nodes[path]
            if (self.core.is_instance_of(node, self.META['ChiCredentials']) or self.core.is_instance_of(node, self.META['FabricCredentials'])):
                logger.info(self.core.get_attribute(node, "name"))
                self.credentials.append(node)
        
        for node in self.credentials:
            if "fabric" in self.core.get_attribute(node, "name").lower():
                self.credential_file += "\nfabric:"
                fabric_attributes = self.core.get_attribute_names(node)
                logger.info("attribute names are: ", fabric_attributes)
                for attribute_name in fabric_attributes:
                    if attribute_name != "name":
                        self.credential_file += f'\n\t{attribute_name}: {self.core.get_attribute(node, attribute_name)}' 
            elif "chi" in self.core.get_attribute(node, "name").lower():
                self.credential_file += "\nchi:"
                chi_attributes = self.core.get_attribute_names(node)
                logger.info("attribute names are: ", chi_attributes)
                for attribute_name in chi_attributes:
                    if attribute_name != "name":
                        self.credential_file += f'\n\t{attribute_name}: {self.core.get_attribute(node, attribute_name)}'    
        
        logger.info(self.credential_file)
        commit_info = self.util.save(self.root_node, self.commit_hash, 'master', 'Python plugin updated the model')
        logger.info('committed :{0}'.format(commit_info))
        self.add_file("fabric" + '_credentials.yml', self.credential_file)   

        
            




                



        
