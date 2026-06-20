# MultiService Backend

A Django REST backend for a multi-service appointment booking platform. It provides APIs for authentication, service discovery, providers, bookings, reviews, and related business rules.

## Project Role

This repository is the backend API for the full MultiService Appointment Booking System.

Related frontend repository:
- https://github.com/GeethikaSai-24/multiservice-app

## Features

- Custom user model with role support
- JWT-based authentication
- Service category and service APIs
- Provider listing and filtering
- Booking creation and cancellation
- Duplicate slot prevention
- Daily availability checks for providers/doctors
- Review creation, update, delete, and listing
- Modular Django app structure for future extension

## Tech Stack

- Python
- Django
- Django REST Framework
- Simple JWT
- SQLite
- CORS Headers

## Main Apps

- `users/` user accounts, roles, login, and password flows
- `services/` service categories and services
- `providers/` provider profiles and filtering
- `bookings/` booking management and availability checks
- `reviews/` review management
- `doctors/` doctor profile support
- `payments/` placeholder for future payment integration
- `config/` project settings and URL configuration

## API Areas

- `api/users/`
- `api/services/`
- `api/providers/`
- `api/bookings/`
- `api/reviews/`

## Getting Started

1. Create and activate a virtual environment.
2. Install project dependencies.
3. Apply migrations:
   `python manage.py migrate`
4. Start the server:
   `python manage.py runserver`

## Notes

- The current setup uses SQLite for development.
- JWT authentication is configured through Django REST Framework.
- The `payments` app exists as a foundation for future payment support.

## Resume Summary

A modular Django REST backend for a multi-service booking platform, implementing authentication, provider discovery, booking logic, reviews, and appointment availability rules.
