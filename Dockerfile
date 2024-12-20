# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variable to indicate the application is running in Docker
ENV RUNNING_IN_DOCKER=true

# Make port 8501 available to the world outside this container
EXPOSE 8501

# Run the application
CMD ["sh", "-c", "python /app/populate_db.py && streamlit run /app/streamlit_app.py"]