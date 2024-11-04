# Use the official Python image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Install pipenv
RUN pip install pipenv

# Copy only Pipfile and Pipfile.lock first for caching
COPY Pipfile Pipfile.lock /app/

# Install dependencies
RUN pipenv install --deploy --system

# Copy the rest of the application code
COPY . /app

# Expose the Flask/Gunicorn port
EXPOSE 5000

# Start the application with Gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]