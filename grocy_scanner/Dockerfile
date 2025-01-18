FROM ghcr.io/hassio-addons/base:12.2.4

# Set labels used in the addon
LABEL \
    io.hass.name="Grocy Item Scanner" \
    io.hass.description="A Home Assistant addon for scanning items into Grocy." \
    io.hass.version="1.0.0" \
    maintainer="Aesgarth <aesgarth@aesgarth.co.uk>"

# Setup working directory
WORKDIR /app

# Install dependencies
RUN apk add --no-cache \
    python3 \
    py3-pip \
    nginx \
    bash

# Copy addon files
COPY . /app

# Ensure run.sh is executable
RUN chmod +x /app/run.sh

# Install Python dependencies
RUN pip3 install -r requirements.txt

# Expose ingress port
EXPOSE 3456

# Entrypoint
CMD ["bash", "/app/run.sh"]
