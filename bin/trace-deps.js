#!/usr/bin/env node

/**
 * Utility script to leverage jpsm/SystemJS' power to build the depcache
 * for a given package.
 *
 * This traces the module and extracts the relative paths to all the
 * files used.
 */

var fs = require('fs');
var Builder = require('jspm').Builder;


var jsapp = process.argv[2];  // 0 is node, 1 is the file


var builder = new Builder();
builder.trace(jsapp).then(function(trace) {
    var deps = {}
    for( var jsapp in trace ) {
        deps[jsapp] = {
            name: jsapp,
            timestamp: trace[jsapp].timestamp,
            path: trace[jsapp].path
        };
    }
    process.stdout.write(JSON.stringify(deps, null));
});
