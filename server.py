from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import requests
import pandas as pd
import datetime
from io import StringIO

app = FastAPI()

access_token = None


def get_access_token():
    global access_token
    if not access_token:
        url = "https://api.baubuddy.de/index.php/login"
        payload = {"username": "365", "password": "1"}
        headers = {
            "Authorization": "Basic QVBJX0V4cGxvcmVyOjEyMzQ1NmlzQUxhbWVQYXNz",
            "Content-Type": "application/json",
        }
        response = requests.post(url, json=payload, headers=headers)
        access_token = response.json()["oauth"]["access_token"]
    return access_token


@app.post("/vehicles/")
async def process_vehicles(file: UploadFile):
    try:
        access_token = get_access_token()
        csv_data = await file.read()
        df = pd.read_csv(StringIO(csv_data.decode("utf-8")))

        api_url = "https://api.baubuddy.de/dev/index.php/v1/vehicles/select/active"
        headers = {"Authorization": f"Bearer {access_token}"}
        api_response = requests.get(api_url, headers=headers).json()

        merged_data = pd.merge(df, pd.DataFrame(api_response), on="rnr")
        merged_data = merged_data.dropna(subset=["hu"])

        label_color_map = {}
        for label_id in merged_data["labelIds"]:
            label_url = f"https://api.baubuddy.de/dev/index.php/v1/labels/{label_id}"
            label_response = requests.get(label_url, headers=headers).json()
            if len(label_response) > 0:
                label_color_map[label_id] = label_response[0].get("colorCode", None)

        def color_row(row):
            if row["hu"] <= 3:
                return "background-color: #007500"
            elif row["hu"] <= 12:
                return "background-color: #FFA500"
            else:
                return "background-color: #b30000"

        if "labelIds" in df.columns:
            merged_data["labelColor"] = merged_data["labelIds"].map(label_color_map)
            merged_data = merged_data.style.applymap(
                color_row, subset=["hu"]
            ).hide_columns(["labelIds"])

        current_date = datetime.datetime.now().isoformat()[:-7]
        excel_filename = f"vehicles_{current_date}.xlsx"
        merged_data.to_excel(excel_filename, index=False)

        return JSONResponse(content={"message": "Success", "file_name": excel_filename})
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)
