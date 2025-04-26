# Use official Python image as base
FROM python:3.11-slim

# Set the working directory
WORKDIR .

# Copy the current directory contents into the container
COPY . .

# Install Flask
RUN pip install flask
RUN pip install redis openai elasticsearch==8.12.1
RUN pip install psycopg2-binary
RUN pip install rq==1.11.0 boto3 python-dotenv

# Expose the port Flask runs on
EXPOSE 5000

# Command to run the app
CMD ["python", "main.py"]