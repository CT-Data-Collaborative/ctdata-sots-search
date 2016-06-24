'use strict';
var gulp = require('gulp'),
    shell = require('gulp-shell'),
    exec = require('gulp-exec');

gulp.task('build', shell.task([
    'docker-compose build'
]));

gulp.task('up', ['build'], shell.task([
    'docker-compose up -d'
]));

gulp.task('test', ['build'], shell.task([
   'docker-compose run web py.test -v sots/sots_tests.py'
]));

gulp.task('coverage', ['build'], shell.task([
    'docker-compose run web py.test --cov-report term-missing --cov=sots sots/sots_tests.py'
]));
