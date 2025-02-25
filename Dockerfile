# Galaxy Image Analysis Docker Image

FROM bgruening/galaxy:24.2

MAINTAINER Leonid Kostrykin, leonid.kostrykin@bioquant.uni-heidelberg.de

ENV GALAXY_CONFIG_BRAND="Galaxy Imaging" \
    ENABLE_TTS_INSTALL=True

# Install imaging tools
ADD tools.yml $GALAXY_ROOT/tools.yaml
RUN install-tools $GALAXY_ROOT/tools.yaml && \
    /tool_deps/_conda/bin/conda clean --tarballs
