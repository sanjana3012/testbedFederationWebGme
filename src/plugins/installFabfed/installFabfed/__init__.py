"""
This is where the implementation of the plugin code goes.
The installFabfed-class is imported from both run_plugin.py and run_debug.py
"""
import sys
import logging
from webgme_bindings import PluginBase

# Setup a logger
logger = logging.getLogger('installFabfed')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)  # By default it logs to stderr..
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class installFabfed(PluginBase):
    def main(self):
        core = self.core
        root_node = self.root_node
        active_node = self.active_node
        sh_file = '''
        pip install virtualenv
        virtualenv -p python3.9 myenv
        # For Windows:
        # myenv\Scripts\activate
        # For macOS and Linux:
        source myenv/bin/activate
        git clone git@github.com:fabric-testbed/fabfed.git
        cd fabfed/
        pip install -r requirements.txt
        pip install -e .
        '''

        self.add_file("install_fabfed.sh", sh_file)


        commit_info = self.util.save(root_node, self.commit_hash, 'master', 'Python plugin updated the model')
        logger.info('committed :{0}'.format(commit_info))
