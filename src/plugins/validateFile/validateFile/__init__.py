"""
This is where the implementation of the plugin code goes.
The validateFile-class is imported from both run_plugin.py and run_debug.py
"""
import sys
import logging
import os
import subprocess
from webgme_bindings import PluginBase

# Setup a logger
logger = logging.getLogger('validateFile')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)  # By default it logs to stderr..
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class validateFile(PluginBase):
    def main(self):
        core = self.core
        root_node = self.root_node
        active_node = self.active_node

        name = core.get_attribute(active_node, 'name')

        logger.info('ActiveNode at "{0}" has name {1}'.format(core.get_path(active_node), name))

        core.set_attribute(active_node, 'name', 'newName')

        commit_info = self.util.save(root_node, self.commit_hash, 'master', 'Python plugin updated the model')
        logger.info('committed :{0}'.format(commit_info))
        self.validate(name)

    def validate(self, name):

        session_name=name
        validate_command = f'fabfed workflow -s {session_name} -validate'
        # Change the directory to where you want to run the command
        os.chdir(os.path.expanduser('~/testbedFederationWebGme/fabfed/examples'))

        # Run the command
        subprocess.run(validate_command, shell=True, check=True)

        
