# Use a lightweight Python 3.13 image (same Python version used to train the model in Colab)
FROM python:3.13-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file first so the dependency layer is cached between builds
COPY requirements.txt .

# Install dependencies from the requirements file without using cache to reduce image size
RUN pip install --no-cache-dir -r requirements.txt

# Copy the remaining files (app.py and the serialized model) into the container
COPY . .

# Start the application using Gunicorn with 4 worker processes
# - `-w 4`: Uses 4 worker processes for handling requests
# - `-b 0.0.0.0:7860`: Binds the server to port 7860 on all network interfaces
# - `app:superkart_api`: Runs the Flask app instance named `superkart_api` in `app.py`
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:7860", "app:superkart_api"]
