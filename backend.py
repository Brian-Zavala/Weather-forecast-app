import requests

API_KEY = "6d88b1e8f4d58057b86ef9f8375c356a"



def get_data(place, days=None, kind=None):
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={place}&units=imperial&appid={API_KEY}"
    response = requests.get(url)
    data = response.json()
    filtered_data = data["list"]
    if days is not None:
        fc_days = 8 * days
        filtered_data = filtered_data[:fc_days]
    if kind == "Temperature":
        filtered_data = [dict["main"]["temp"] for dict in filtered_data]
    if kind == "Sky":
        filtered_data = [dict["weather"][0]["main"] for dict in filtered_data]
    return filtered_data


if __name__ == '__main__':
    print(get_data(place="Houston", days=3, kind="Temperature"))