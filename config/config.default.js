'use strict';

var config = require('./config.webgme'),
    validateConfig = require('webgme/config/validator');
    const path = require('path');

// Add/overwrite any additional settings here
config.server.port = 8888;
// config.mongo.uri = 'mongodb://127.0.0.1:27017/webgme_my_app';
// Plugins
config.plugin.allowServerExecution = true;


// Seeds
// config.seedProjects.enable = true;
// config.seedProjects.basePaths = ["./seeds"]

// Icons
// config.visualization.svgDirs = ['./icons/png'];

// config.plugin.basePaths.push('src/common');
// config.visualization.decoratorPaths.push('./src/decorators');



config.visualization.svgDirs = [path.join(__dirname, '../icons/png')];

validateConfig(config);
config.plugin.allowServerExecution = true
module.exports = config;
