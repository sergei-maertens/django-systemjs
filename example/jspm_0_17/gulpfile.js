'use strict';

var gulp = require('gulp'),
    watch = require('gulp-watch');

var static_src = [
    './*/static/**/*.js',
    '!./{staticfiles,staticfiles/**}',
    './static/**/*.js'
];


// watch task
gulp.task('default',function() {
    gulp.src(static_src, {base: '.'})
        .pipe(watch(static_src))
        .pipe(gulp.dest('staticfiles'));
});
