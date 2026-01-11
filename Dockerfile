# Galaxy Image Analysis — Docker Image
# https://github.com/bgruening/docker-galaxy?tab=readme-ov-file#extending-the-docker-image--toc

FROM quay.io/bgruening/galaxy:25.1.1
LABEL org.opencontainers.image.authors="leonid.kostrykin@bioquant.uni-heidelberg.de"
ENV GALAXY_CONFIG_BRAND="Galaxy Image Analysis"

# Hide categories
RUN apt update
RUN apt install -y xmlstarlet
RUN xmlstarlet ed -L -d '/toolbox/section[@id="convert"]' /etc/galaxy/tool_conf.xml
RUN xmlstarlet ed -L -d '/toolbox/section[@id="fetchAlignSeq"]' /etc/galaxy/tool_conf.xml
RUN xmlstarlet ed -L -d '/toolbox/section[@id="bxops"]' /etc/galaxy/tool_conf.xml
RUN xmlstarlet ed -L -d '/toolbox/section[@id="hgv"]' /etc/galaxy/tool_conf.xml
RUN xmlstarlet ed -L -d '/toolbox/section[@id="plots"]' /etc/galaxy/tool_conf.xml
RUN sed -i 's|^\( *\)#\(\s*display_builtin_converters:\s*\).*|\1\2false|' /etc/galaxy/galaxy.yml
RUN apt purge -y xmlstarlet
RUN rm -rf /var/cache/apt/archives /var/lib/apt/lists/*

# Install GIA tools
WORKDIR /galaxy
ADD tools.yml "$GALAXY_ROOT_DIR/tools.yml"
RUN add-tool-shed --url 'http://testtoolshed.g2.bx.psu.edu/' --name 'Test Tool Shed'
RUN install-tools "$GALAXY_ROOT_DIR/tools.yml"

# Mark folders as imported from the host.
VOLUME ["/export/", "/data/", "/var/lib/docker"]

# Expose port 80 (webserver), 21 (FTP server)
EXPOSE :80
EXPOSE :21

# Autostart script that is invoked during container start
CMD ["/usr/bin/startup2"]
