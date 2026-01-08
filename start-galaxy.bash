# This is a custom startup script that is used for installation of tools when building the image,
# until the original script `install-tools` in the upstream image is fixed:
#
# https://github.com/bgruening/docker-galaxy/issues/620

set -e

service postgresql start

source /galaxy_venv/bin/activate

PYTHONPATH=lib GALAXY_CONFIG_FILE=/etc/galaxy/galaxy.yml gunicorn \
    'galaxy.webapps.galaxy.fast_factory:factory()' \
    --timeout 300 \
    --pythonpath lib \
    -k galaxy.webapps.galaxy.workers.Worker \
    -b localhost:8080 \
    --workers=1 \
    --config python:galaxy.web_stack.gunicorn_config \
    --preload &

while true; do
    status=$(curl -o /dev/null -s -w "%{http_code}\n" http://localhost:8080 || true)

    # Normalize empty status code to "000"
    [ -z "$status" ] && status="000"

    echo "Status code: $status"
    if [ "$status" = "200" ]; then
        echo "Galaxy is up."
        exit 0
    fi
    sleep 2
done
