FROM python:3.13-alpine
WORKDIR /app
COPY app/ .
RUN pip install --no-cache-dir -r requirements.txt
CMD ["fastapi", "run", "--root-path", "mailing-api", "--workres", "4" ]
