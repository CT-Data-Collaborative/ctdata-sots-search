'use strict';
var gulp = require('gulp'),
    shell = require('gulp-shell'),
    exec = require('gulp-exec'),
    sass = require('gulp-sass');

gulp.task('build', ['sass'], shell.task([
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


gulp.task('js_dependencies', function() {
    gulp.src([
        'node_modules/jquery/dist/jquery.min.js',
        'node_modules/bootstrap/dist/js/bootstrap.min.js',
        'node_modules/bootstrap-datepicker/dist/js/bootstrap-datepicker.js'
    ]).pipe(gulp.dest('web/sots/static/js/libs'));
});

gulp.task('css_dependencies', function() {
   gulp.src([
       'node_modules/bootstrap/dist/css/bootstrap.min.css',
       'node_modules/font-awesome/css/font-awesome.min.css',
       'node_modules/bootstrap-datepicker/dist/css/bootstrap-datepicker3.min.css'
   ]).pipe(gulp.dest('web/sots/static/css'));
});

gulp.task('fonts', function() {
    gulp.src([
        'node_modules/font-awesome/fonts/*.*'
    ]).pipe(gulp.dest('web/sots/static/fonts'));
});


gulp.task('sass', function() {
    gulp.src('src/sass/sots.scss')
     .pipe(sass().on('error', sass.logError))
     .pipe(gulp.dest('web/sots/static/css'));
});


gulp.task('depends', ['js_dependencies', 'css_dependencies', 'fonts'], function() {
});

gulp.task('default', function() {
    gulp.run('build');
});

