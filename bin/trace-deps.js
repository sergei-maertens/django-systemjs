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
        var skip = trace[jsapp] === false; // e.g. with google maps, see #13
        deps[jsapp] = {
            name: jsapp,
            timestamp: skip ? null : trace[jsapp].timestamp,
            path: skip ? null : trace[jsapp].path,
            skip: skip
        };
    }
    process.stdout.write(JSON.stringify(deps, null));
});
