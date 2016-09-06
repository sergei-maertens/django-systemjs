'use strict';

var gulp = require('gulp'),
    watch = require('gulp-watch'),
    rename = require('gulp-rename');

/**
 * exactly the same paths as in the DJANGO settings. You could manage this with
 * environment variables to be DRY
 */
var STATIC_ROOT = './staticfiles';
var STATICFILES_DIRS = [
    './static/',
];

var static_src = [
    './*/static/**/*.js', // APP_DIRS
    '!./{staticfiles,staticfiles/**}', // exclude STATIC_ROOT (otherwise we end up with infite loops)
].concat(STATICFILES_DIRS.map(function(dir) { // include all js files in STATICFILES_DIRS
    return dir + '**/*.js';
}));


// watches STATICFILES_DIRS
gulp.task('collectstatic', function() {
    return watch(static_src, {verbose: true, base: './static'})
        .pipe(rename(function(file) {
            var bits = file.dirname.split('/');
            // strip off '..', 'appname' and 'static' - .. comes from base ./static
            file.dirname = bits.slice(3).join('/');
            return file;
        }))
        .pipe(gulp.dest(STATIC_ROOT));
});


// watch task
gulp.task('default', ['collectstatic']);
