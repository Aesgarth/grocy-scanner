FROM python:3.11-alpine

# Install dependencies
RUN apk add --no-cache \
    nginx supervisor

# Set working directory
WORKDIR /app

# Copy application and configuration files
COPY app /app
COPY web /app/web
COPY nginx.conf /etc/nginx/nginx.conf
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY run.sh /app/run.sh

# Install Python dependencies
RUN pip install -r /app/requirements.txt

# Expose ingress port
EXPOSE 3456

# Start services
CMD ["/app/run.sh"]
