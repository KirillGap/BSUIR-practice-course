import requests


url = 'http://api.openweathermap.org/data/2.5/weather?q=local&APPID=de4d2422f04c27515681eec4b5741348'


def main():
    print(requests.get(url).status_code)  # 200
    print(requests.get(url[:-1]).status_code)  # 401
    print(requests.get(url.replace('?', '/notExistsPage?')).status_code)  # 404
    print(requests.delete(url).status_code)  # 405


if __name__ == '__main__':
    main()
