"""
This is where the implementation of the plugin code goes.
The fileGenerator-class is imported from both run_plugin.py and run_debug.py
"""
import sys
import logging
from webgme_bindings import PluginBase
import yaml

# Setup a logger
logger = logging.getLogger('createCredentialFile')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)  # By default it logs to stderr..
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class createCredentialFile(PluginBase):
    def main(self):      
        self.nodes = {}
        self.credentials = []
        self.credentials_dict={}
        
        

        nodes_list = self.core.load_sub_tree(self.active_node)        
        for node in nodes_list:
            self.nodes[self.core.get_path(node)] = node
        
        
        self.fetch_credentials()

    def fetch_credentials(self):
        for path in self.nodes:
            node = self.nodes[path]
            if (self.core.is_instance_of(node, self.META['ChiCredentials']) or self.core.is_instance_of(node, self.META['FabricCredentials'])):
                logger.info(self.core.get_attribute(node, "name"))
                self.credentials.append(node)
        
        for node in self.credentials:
            if self.core.is_instance_of(node,self.META['FabricCredentials']):
                if "fabric" not in self.credentials_dict:
                    self.credentials_dict["fabric"]={}
                
                fabric_attributes = self.core.get_attribute_names(node)
                logger.info("attribute names are: ", fabric_attributes)
                for attribute_name in fabric_attributes:
                    if attribute_name != "name":
                        self.credentials_dict["fabric"][f"{attribute_name}"]= self.core.get_attribute(node, attribute_name)

            elif self.core.is_instance_of(node,self.META['ChiCredentials']):
                if "chi" not in self.credentials_dict:
                    self.credentials_dict["chi"]={}
                
                chi_attributes = self.core.get_attribute_names(node)
                logger.info("attribute names are: ", chi_attributes)
                for attribute_name in chi_attributes:
                    if attribute_name=="project_id":
                        self.credentials_dict["chi"]["project_id"]={}
                        if self.core.get_attribute(node, "project_site")=="uc":
                            if "uc" not in self.credentials_dict["chi"]["project_id"]:
                                self.credentials_dict["chi"]["project_id"]["uc"]=self.core.get_attribute(node, "project_id")
                        elif self.core.get_attribute(node, "project_site")=="tacc":
                            if "uc" not in self.credentials_dict["chi"]["project_id"]:
                                self.credentials_dict["chi"]["project_id"]["tacc"]=self.core.get_attribute(node, "project_id")

                    elif attribute_name not in ["name", "project_site"]:
                        self.credentials_dict["chi"][f"{attribute_name}"]= self.core.get_attribute(node, attribute_name)
            
   
        
        # logger.info(self.credential_file)
        cred_file = yaml.dump(self.credentials_dict, default_flow_style=False)
        self.add_file("fabfed_credentials.yml", cred_file)           
        commit_info = self.util.save(self.root_node, self.commit_hash, 'master', 'Python plugin updated the model')
        logger.info('committed :{0}'.format(commit_info))

        
            




                



        
