# Use the official lightweight Nginx image as the base
FROM nginx:alpine

# Copy the static website files to the Nginx HTML directory
COPY . /usr/share/nginx/html/

# Expose port 80 to the outside world
EXPOSE 80

# Nginx starts automatically when the container runs, so no CMD is needed
