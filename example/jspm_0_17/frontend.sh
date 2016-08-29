# ensure that the dev dependencies are up to date
npm install

# collect the static files, and remove the old files first
python manage.py collectstatic -c --noinput

# install the front-end dependencies (JS libs)
jspm install

# bundle the apps into efficient bundles
python manage.py systemjs_bundle
