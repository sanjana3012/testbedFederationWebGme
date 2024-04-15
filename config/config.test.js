/*jshint node: true*/
/**
 * @author lattmann / https://github.com/lattmann
 */

var config = require('./config.default');

config.server.port = 9001;
config.mongo.uri = 'mongodb://mongodb/webgmedb';

module.exports = config;
