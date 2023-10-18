## 1. Run Server:

```sh
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

## 2. Run Client:

```sh
python client.py vehicles.csv http://localhost:8000/vehicles/
```
