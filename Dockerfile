FROM python:3

# Set working directory inside the container
WORKDIR /code

# Copy requirements and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Expose port FastAPI will run on
EXPOSE 8000

# Start the app
CMD ["uvicorn", "Library_Management.main:app", "--host", "0.0.0.0", "--port", "8000"]
