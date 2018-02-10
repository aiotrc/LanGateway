from requests import post


def send_data_https():
    result = post('https://localhost:5000/data', json=dict(
        token='eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE1MjAyNTAwMDIsImlhdCI6MTUxNzY1ODAwMiwic3ViIjoxfQ.L5SZVHC1Pc2jdV88SP2a0Son6jDbUnSCbtaq8I_P9fQ',
        data='{"temp":"20"}'
    ), verify='server.pem')
    print(result.text)


if __name__ == '__main__':
    send_data_https()
