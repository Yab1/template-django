FROM python:3.12.4

# Fix Python printing
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /usr/src/app

# Copy the requirements directory into the container
COPY requirements/ /requirements/
RUN pip install --no-cache-dir -r /requirements/local.txt

# Copy the rest of the Django project
COPY . .

# Make entrypoint script executable
RUN chmod +x entrypoint.sh

# Use entrypoint script
CMD ["/usr/src/app/entrypoint.sh"]