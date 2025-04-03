FROM python

WORKDIR /app

COPY /src /app/src
COPY /requirements.txt /.env /app/

# Install rust for fastapi-cache2 >= 0.2.2
RUN apt-get update && apt-get install -y --no-install-recommends curl build-essential \
    && curl https://sh.rustup.rs -sSf | sh -s -- -y \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

ENV PATH="/root/.cargo/bin:${PATH}"

RUN pip install -r requirements.txt

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]