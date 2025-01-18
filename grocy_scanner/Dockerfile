FROM ghcr.io/hassio-addons/base:17.1.0

# Set working directory
WORKDIR /app

# Install Python and pip
RUN apk add --no-cache python3 py3-pip

# Copy application and configuration files
COPY app /app
COPY web /app/web
COPY nginx.conf /etc/nginx/nginx.conf
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY run.sh /app/run.sh

# Ensure run.sh is executable
RUN chmod +x /app/run.sh

# Install Python dependencies
RUN pip3 install --no-cache-dir -r /app/requirements.txt

# Expose ingress port
EXPOSE 3456

ENV API_KEY=${api_key}

# Start services
CMD ["/app/run.sh"]
