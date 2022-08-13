import requests
from pprint import pprint

HOST = 'http://127.0.0.1:5000'


""" POST """
response = requests.post(f'{HOST}/users/',
                        json={'name': 'User1',
                              'password': '1234'})
pprint(response.status_code)
pprint(response.text)

# response = requests.post(f'{HOST}/advertisements/',
#                         json={'header': 'Header 1',
#                               'description': 'Descripiton 1',
#                               'owner_id': 1})
# pprint(response.status_code)
# pprint(response.text)


""" GET """

# response = requests.get(f'{HOST}/users/1')
# pprint(response.status_code)
# pprint(response.text)
#
# response = requests.get(f'{HOST}/advertisements/1')
# pprint(response.status_code)
# pprint(response.text)


""" PATCH """

# response = requests.patch(f'{HOST}/users/1',
#                           json={'name': 'user1_v2'})
# pprint(response.status_code)
# pprint(response.text)
#
# response = requests.patch(f'{HOST}/advertisements/1',
#                           json={'header': 'Header 1 v2',
#                                 'description': 'Description 1 v2'})
# pprint(response.status_code)
# pprint(response.text)


""" DELETE """

# response = requests.delete(f'{HOST}/users/1')
# pprint(response.status_code)
# pprint(response.text)
#
# response = requests.delete(f'{HOST}/advertisements/1')
# pprint(response.status_code)
# pprint(response.text)