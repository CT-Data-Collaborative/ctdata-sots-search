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

//
// gulp.task('js_dependencies', function() {
//     gulp.src([
//         'node_modules/angular/angular.min.js',
//         'node_modules/angular-animate/angular-animate.min.js',
//         'node_modules/angular-ui-bootstrap/dist/ui-bootstrap-tpls.js',
//         'node_modules/d3/d3.min.js',
//         'node_modules/d3-tip/index.js',
//         'node_modules/d3-jetpack/d3-jetpack.js',
//         'node_modules/ng-lodash/build/ng-lodash.min.js',
//         'node_modules/tether/dist/js/tether.min.js',
//         'node_modules/jquery/dist/jquery.min.js',
//         'src/static/js/**/visualizations/*.js'
//     ]).pipe(gulp.dest('dist/js/libs'));
// });
//
// gulp.task('css_dependencies', function() {
//    gulp.src([
//        'node_modules/angular-ui-bootstrap/dist/ui-bootstrap-csp.css',
//        'node_modules/tether/dist/css/tether.min.css'
//    ]).pipe(gulp.dest('dist/css'));
// });
//
// gulp.task('js', function() {
//     gulp.src(['src/static/js/**/module.js', 'src/static/js/**/dataviz/*.js'])
//      .pipe(sourcemaps.init())
//       .pipe(concat('app.js'))
//      .pipe(gulp.dest('./dist/js/'))
// });


gulp.task('sass', function() {
    gulp.src('src/sass/sots.scss')
     .pipe(sass().on('error', sass.logError))
     .pipe(gulp.dest('web/sots/static/css'));
});

//
// gulp.task('build', ['js', 'js_dependencies', 'css_dependencies', 'sass'], function() {
//     gulp.src('src/static/images/logo.svg').pipe(gulp.dest('dist/images/'));
//     gulp.src(['src/data/*.json', 'src/data/*.geojson']).pipe(gulp.dest('dist/data/'));
//     gulp.src(['src/data/pdfs/*']).pipe(gulp.dest('dist/data/pdfs'));
//     gulp.src(['src/index.html']).pipe(gulp.dest('dist/'));
//     gulp.src(['src/static/partials/*.html']).pipe(gulp.dest('dist/partials'));
// });

gulp.task('default', function() {
    gulp.run('build');
});

