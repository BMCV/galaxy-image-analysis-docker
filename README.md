[![Update](https://github.com/BMCV/galaxy-image-analysis-docker/actions/workflows/update.yml/badge.svg)](https://github.com/BMCV/galaxy-image-analysis-docker/actions/workflows/update.yml)
[![Build](https://github.com/BMCV/galaxy-image-analysis-docker/actions/workflows/build.yml/badge.svg)](https://github.com/BMCV/galaxy-image-analysis-docker/actions/workflows/build.yml)

# Docker Image for Galaxy Image Analysis

Galaxy Image Analysis: https://github.com/BMCV/galaxy-image-analysis

Building the image:
```bash
docker build -t galaxy-image-analysis .
```

Running the container:
```bash
 docker run --rm --privileged -p 8080:80 -p 8021:21 -p 8022:22 \
    kostrykin/galaxy-image-analysis:latest
 ```
or just `galaxy-image-analysis` for the locally built image.

Also see the [instructions for the Galaxy base image](https://github.com/bgruening/docker-galaxy?tab=readme-ov-file#table-of-contents-). 
