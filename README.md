# Django App Template

This repository serves as a template for quickly setting up Django applications. It includes a variety of pre-configured features and tools to streamline development.

## Features

- **Docker Compose**: Easily manage your PostgreSQL database with Docker.
- **Authentication**: Pre-configured authentication setup for secure user management.
- **Django REST Framework**: Build powerful APIs with ease.
- **DRF Spectacular**: Automatically generate OpenAPI schema for your APIs.
- **Django Guardian**: Implement object-level permissions.
- **Django Easy Audit**: Track changes in your models with audit logging.
- **Inspired by Hacksoft Django Style Guide**: Follow best practices and coding standards.

## Getting Started

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/) installed on your machine.
- Python 3.12+ (for local development).

### Setup

1. **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/django-app-template.git
    cd django-app-template
    ```
2. **Create a logs directory:**
    ```bash
    mkdir logs
    ```
3. **Install Python dependencies:**
    ```bash
    make install-all-requirements
    ```
4. **Copy the environment file:**
    ```bash
    cp .env.example .env
    ```
5. **Start the Docker containers:**
    ```bash
    docker-compose up -d
    ```
6. **Run migrations:**
    ```bash
    make migrate
    ```
7. **Create a superuser (optional):**
    ```bash
    make superuser
    ```
8. **Access the development server:**
   Visit `http://localhost:8000` in your web browser.

## Usage

- Use the Django admin interface for managing users and models.
- Access your API endpoints via the `/api/` path.
- Generate the API schema with:
    ```bash
    make generate-schema
    ```

## Contributing

Feel free to make improvements or add features! Please submit a pull request for any major changes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
