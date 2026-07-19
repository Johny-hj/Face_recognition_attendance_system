FROM continuumio/miniconda3:latest

WORKDIR /app

# Install dlib and face_recognition from conda-forge (pre-compiled binaries)
RUN conda install -c conda-forge dlib face_recognition -y

# Copy requirements
COPY requirements.txt .

# Remove face-recognition from requirements.txt since conda already installed it
RUN sed -i '/face-recognition/d' requirements.txt

# Install remaining dependencies via pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose port (Render defaults to 10000 or reads PORT env)
EXPOSE 10000

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]
