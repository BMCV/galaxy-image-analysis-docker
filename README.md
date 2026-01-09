# Docker Image for Galaxy Image Analysis

Building the image:
```bash
docker build -t galaxy-image-analysis .
```

Running the container:
```bash
 docker run --rm --privileged \
    -p 8080:80 -p 8021:21 -p 8022:22 \
    galaxy-image-analysis
 ```
