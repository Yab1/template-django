# Clean up migration files
.PHONY: clean-migrations
clean-migrations:
	@echo "Cleaning up migration files..."
	@find core -path "*/migrations/*.py" -not -name "__init__.py" -delete
	@find core -path "*/migrations/*.pyc" -delete

# Collect static files
.PHONY: collectstatic
collectstatic:
	@echo "Collecting static files..."
	@python manage.py collectstatic --noinput

# Install all dependencies (production and development)
.PHONY: install-all-requirements
install-all-requirements:
	@echo "Installing all dependencies (production and development)..."
	@pip install -r requirements/base.txt -r requirements/local.txt

# Install and configure pre-commit hooks
.PHONY: install-pre-commit
install-pre-commit:
	@echo "Installing and configuring pre-commit hooks..."
	@pre-commit uninstall
	@pre-commit install

# Install production dependencies
.PHONY: install-production-requirements
install-production-requirements:
	@echo "Installing production dependencies..."
	@pip install -r requirements/base.txt

# Run linters
.PHONY: lint
lint:
	@echo "Running linters..."
	@pre-commit run --all-files

# Create migration files
.PHONY: migrations
migrations:
	@echo "Creating migration files..."
	@python manage.py makemigrations

# Apply migrations
.PHONY: migrate
migrate:
	@echo "Applying migrations..."
	@python manage.py migrate

# Run the development server
.PHONY: run-server
run-server:
	@echo "Running the development server..."
	@python manage.py runserver

# Open the Django shell
.PHONY: shell
shell:
	@echo "Opening the Django shell..."
	@python manage.py shell

# Create a superuser
.PHONY: superuser
superuser:
	@echo "Creating a superuser..."
	@python manage.py createsuperuser

# Update project (install dependencies, apply migrations, install pre-commit hooks)
.PHONY: update
update: install-all-requirements migrate install-pre-commit
	@echo "Updating project..."
