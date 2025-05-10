const gulp        = require('gulp');
const sass        = require('gulp-sass')(require('sass'));
const pug         = require('gulp-pug');
const browserSync = require('browser-sync').create();

// Compile SCSS → static/css
function compileSass() {
  return gulp.src('src/scss/**/*.scss')
    .pipe(sass().on('error', sass.logError))
    .pipe(gulp.dest('static/css'))
    .pipe(browserSync.stream());
}

// Compile all pages → static/*.html
function compilePug() {
  return gulp.src('src/pug/pages/**/*.pug')
    .pipe(pug({
      basedir: 'src/pug',
      pretty: false
    }))
    .pipe(gulp.dest('static/'))
    .pipe(browserSync.stream());
}

// Serve & watch
function serve() {
  browserSync.init({
    server: { baseDir: 'static' },
    port: 3000
  });
  gulp.watch('src/scss/**/*.scss', compileSass);
  gulp.watch('src/pug/**/*.pug', compilePug);
  gulp.watch('static/*.html').on('change', browserSync.reload);
  gulp.watch('static/css/*.css').on('change', browserSync.reload);
}

exports.default = gulp.series(
  gulp.parallel(compileSass, compilePug),
  serve
);