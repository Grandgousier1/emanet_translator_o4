FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04

# Install system deps
RUN apt-get update && apt-get install -y ffmpeg git && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml .
RUN apt-get update && apt-get install -y python3-pip && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip && pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --without dev

COPY . .

ENTRYPOINT ["emanet-subtitles"]
CMD ["offline"]
