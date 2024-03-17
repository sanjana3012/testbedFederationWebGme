// DO NOT EDIT THIS FILE
// This file is automatically generated from the webgme-setup-tool.
'use strict';


var config = require('webgme/config/config.default'),
    validateConfig = require('webgme/config/validator');

// The paths can be loaded from the webgme-setup.json
config.plugin.basePaths.push(__dirname + '/../src/plugins');
config.seedProjects.basePaths.push(__dirname + '/../src/seeds/fine_tune_seed_1');
config.seedProjects.basePaths.push(__dirname + '/../src/seeds/fabfed');





config.rest.components['BindingsDocs'] = {
  src: __dirname + '/../node_modules/webgme-bindings/src/routers/BindingsDocs/BindingsDocs.js',
  mount: 'bindings-docs',
  options: {}
};

// Visualizer descriptors

// Add requirejs paths
config.requirejsPaths = {
  'BindingsDocs': 'node_modules/webgme-bindings/src/routers/BindingsDocs',
  'webgme-bindings': './node_modules/webgme-bindings/src/common',
  'fabfed_project': './src/common'
};


config.mongo.uri = 'mongodb://127.0.0.1:27017/fabfed_project';
validateConfig(config);
module.exports = config;
