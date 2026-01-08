# Galaxy Image Analysis — Docker Image
# https://github.com/bgruening/docker-galaxy?tab=readme-ov-file#extending-the-docker-image--toc

FROM quay.io/bgruening/galaxy:25.1
LABEL org.opencontainers.image.authors="leonid.kostrykin@bioquant.uni-heidelberg.de"
ENV GALAXY_CONFIG_BRAND="Galaxy Image Analysis"

# Install GIA tools
WORKDIR /galaxy
ADD start-galaxy.bash "$GALAXY_ROOT_DIR/start-galaxy.bash"
ADD tools.yml "$GALAXY_ROOT_DIR/tools.yml"
RUN add-tool-shed --url 'http://testtoolshed.g2.bx.psu.edu/' --name 'Test Tool Shed'
RUN bash "$GALAXY_ROOT_DIR/start-galaxy.bash" && install-tools "$GALAXY_ROOT_DIR/tools.yml"
RUN service postgresql stop
RUN chown -R galaxy:galaxy "/export/galaxy"

# Mark folders as imported from the host.
VOLUME ["/export/", "/data/", "/var/lib/docker"]

# Expose port 80 (webserver), 21 (FTP server)
EXPOSE :80
EXPOSE :21

# Autostart script that is invoked during container start
CMD ["/usr/bin/startup"]
