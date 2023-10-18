import argparse
import requests


def send_csv_to_server(csv_filename, server_url):
    with open(csv_filename, "rb") as file:
        files = {"file": (csv_filename, file)}
        response = requests.post(server_url, files=files)
        return response


def main():
    parser = argparse.ArgumentParser(
        description="Send CSV to server and generate Excel file."
    )
    parser.add_argument(
        "csv_file", help="Path to the CSV file containing vehicle information"
    )
    parser.add_argument("server_url", help="URL of the server API")
    args = parser.parse_args()

    response = send_csv_to_server(args.csv_file, args.server_url)

    if response.status_code == 200:
        data = response.json()
        print(f"File '{data['file_name']}' has been generated successfully.")
    else:
        print(f"Error: {response.text}")


if __name__ == "__main__":
    main()
