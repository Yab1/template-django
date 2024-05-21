# Clean up migration files
.PHONY: clean-migrations
clean-migrations:
	@find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
	@find . -path "*/migrations/*.pyc" -delete

# Collect static files
.PHONY: collectstatic
collectstatic:
	@python manage.py collectstatic

# Install project dependencies
.PHONY: install
install:
	@poetry install

# Install and configure pre-commit hooks
.PHONY: install-pre-commit
install-pre-commit:
	@pre-commit uninstall; poetry run pre-commit install

# Run linters
.PHONY: lint
lint:
	@pre-commit run --all-files

# Create migration files
.PHONY: migrations
migrations:
	@python manage.py makemigrations --verbosity 3

# Apply migrations
.PHONY: migrate
migrate: install
	@python manage.py migrate

# Run the development server
.PHONY: run-server
run-server:
	@poetry run python manage.py runserver

# Open the Django shell
.PHONY: shell
shell:
	@poetry run python manage.py shell

# Create a superuser
.PHONY: superuser
superuser:
	@poetry run python manage.py createsuperuser

# Update project (install dependencies, apply migrations, install pre-commit hooks)
.PHONY: update
update: install migrate install-pre-commit
