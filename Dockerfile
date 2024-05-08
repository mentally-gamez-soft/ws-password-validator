FROM python:3.12.3-bookworm

# Install vi editor in container
RUN apt-get update && apt-get install -y vim net-tools

LABEL Name="Password Scoring Flask APP" Version=$version_number

WORKDIR /ws-password-scoring
COPY requirements.in .
COPY requirements.dev .
RUN python -m pip install --upgrade pip
RUN pip install pip-tools
RUN pip-compile --output-file=requirements.txt requirements.in
RUN pip-compile --output-file=requirements-dev.txt requirements.dev
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements-dev.txt

# root application directory
# COPY .env .
COPY .env.vault .
COPY app.py .

# application core
COPY core ./core

# application tests
# COPY tests ./tests

# static
COPY static ./static

EXPOSE 6019

CMD ["gunicorn", "-b", "0.0.0.0:6019", "app:app"]
