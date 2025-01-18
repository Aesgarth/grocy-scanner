FROM python:3.11-alpine

# Install dependencies
RUN apk add --no-cache \
    nginx supervisor \
    gcc musl-dev python3-dev libffi-dev

# Set working directory
WORKDIR /app

# Copy application and configuration files
COPY /app /app
COPY /web /app/web
COPY /nginx.conf /etc/nginx/nginx.conf
COPY /supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY /run.sh /app/run.sh

# Ensure run.sh is executable
RUN chmod +x /app/run.sh

# Install Python dependencies
RUN pip install -r /app/requirements.txt

# Expose ingress port
EXPOSE 3456

# Debug to verify file structure
RUN ls -l /app

# Start services
CMD ["/run.sh"]
