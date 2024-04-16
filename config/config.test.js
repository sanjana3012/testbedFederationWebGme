/*jshint node: true*/
/**
 * @author lattmann / https://github.com/lattmann
 */

var config = require('./config.default');

config.server.port = 9001;
// config.mongo.uri = 'mongodb://mongo:27017/fabfed_project';
config.mongo.uri = 'mongodb://127.0.0.1:27017/fabfed_project';


module.exports = config;
