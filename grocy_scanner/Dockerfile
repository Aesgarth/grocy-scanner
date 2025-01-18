FROM python:3.11-alpine

# Install dependencies
RUN apk add --no-cache \
    nginx supervisor \
    gcc musl-dev python3-dev libffi-dev

# Set working directory
WORKDIR /app

# Copy application and configuration files
COPY grocy_scanner/app /app
COPY grocy_scanner/web /app/web
COPY grocy_scanner/nginx.conf /etc/nginx/nginx.conf
COPY grocy_scanner/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY grocy_scanner/run.sh /app/run.sh

# Ensure run.sh is executable
RUN chmod +x /app/run.sh

# Install Python dependencies
RUN pip install -r /app/requirements.txt

# Expose ingress port
EXPOSE 3456

# Debug to verify file structure
RUN ls -l /app

# Start services
CMD ["/app/run.sh"]
