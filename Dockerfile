FROM python:3.11-slim
WORKDIR /app

# Explicit file copy with multiple approaches
COPY requirements.txt /app/requirements.txt
RUN ls /app  # Verify file is actually copied
RUN cat /app/requirements.txt  # Confirm file contents

RUN pip install --upgrade pip
RUN pip install -r /app/requirements.txt
COPY . /app
CMD ["python", "app.py"]