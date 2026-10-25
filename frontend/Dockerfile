# Use a lightweight Python 3.13 image (same as the backend for consistency)
FROM python:3.13-slim

# Set the working directory inside the container to /app
WORKDIR /app

# Copy the requirements file first so the dependency layer is cached between builds
COPY requirements.txt .

# Install the Python dependencies listed in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the remaining files (app.py) into the container
COPY . .

# Run the Streamlit app on port 8501 and make it accessible externally
# XSRF protection is disabled so file uploads work through the Codespaces port-forwarding proxy
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.enableXsrfProtection=false"]
