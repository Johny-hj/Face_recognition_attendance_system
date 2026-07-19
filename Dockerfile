FROM continuumio/miniconda3:latest

WORKDIR /app

# Install heavy dependencies from conda-forge (pre-compiled binaries)
RUN conda install -c conda-forge dlib face_recognition pandas numpy opencv openpyxl pillow psycopg2 -y

# Copy requirements
COPY requirements.txt .

# Remove heavy dependencies from requirements.txt since conda already installed them
RUN sed -i '/face-recognition/d' requirements.txt && \
    sed -i '/pandas/d' requirements.txt && \
    sed -i '/numpy/d' requirements.txt && \
    sed -i '/opencv-python-headless/d' requirements.txt && \
    sed -i '/openpyxl/d' requirements.txt && \
    sed -i '/Pillow/d' requirements.txt && \
    sed -i '/psycopg2-binary/d' requirements.txt

# Install remaining dependencies via pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose port (Render defaults to 10000 or reads PORT env)
EXPOSE 10000

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]
