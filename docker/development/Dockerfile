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

# Copy entrypoint to root and make it executable
COPY docker/development/entrypoint.sh entrypoint.sh
RUN chmod +x entrypoint.sh

CMD ["./entrypoint.sh"]