'use strict';
var gulp = require('gulp'),
    shell = require('gulp-shell'),
    exec = require('gulp-exec'),
    sass = require('gulp-sass');


gulp.task('js_dependencies', function() {
    gulp.src([
        'node_modules/jquery/dist/jquery.min.js',
        'node_modules/bootstrap/dist/js/bootstrap.min.js',
        'node_modules/bootstrap-datepicker/dist/js/bootstrap-datepicker.js'
    ]).pipe(gulp.dest('sots/static/js/libs'));
});

gulp.task('css_dependencies', function() {
   gulp.src([
       'node_modules/bootstrap/dist/css/bootstrap.min.css',
       'node_modules/font-awesome/css/font-awesome.min.css',
       'node_modules/bootstrap-datepicker/dist/css/bootstrap-datepicker3.min.css'
   ]).pipe(gulp.dest('sots/static/css'));
});

gulp.task('fonts', function() {
    gulp.src([
        'node_modules/font-awesome/fonts/*.*'
    ]).pipe(gulp.dest('sots/static/fonts'));
});

gulp.task('sass', function() {
    gulp.src('src/sass/sots.scss')
     .pipe(sass().on('error', sass.logError))
     .pipe(gulp.dest('sots/static/css'));
});

gulp.task('images', function() {
    gulp.src('src/images/*.*')
        .pipe(gulp.dest('sots/static/images'));
});

gulp.task('depends', ['js_dependencies', 'css_dependencies', 'fonts', 'images'], function() {
});

gulp.task('default', function() {
    gulp.run('build');
});
