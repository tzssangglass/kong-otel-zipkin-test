## Set up the project

- start kong and otel-collector

```bash
docker-compose up -d
```

- start the backend service

```bash
python backend.py
```

- use another terminal to start the frontend service

```bash
python app.py
```
