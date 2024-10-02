# Use the official Locust image as the base image
FROM locustio/locust:2.15.1

USER root

# Install system dependencies: sudo, ping, telnet
RUN apt-get update && apt-get install -y --no-install-recommends \
    sudo \
    iputils-ping \
    telnet \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /mnt/locust

# Copy the locustfile.py to the working directory
COPY locustfile.py ./

# Copy any other required files (e.g., image files for testing)
COPY receipt.jpg ./

# Expose Locust web interface and test HTTP API ports
EXPOSE 8089
EXPOSE 8000

# Default command to run Locust
# CMD ["locust", "-f", "locustfile.py", "--host=http://localhost:8000"]

