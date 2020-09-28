import requests

headers = {}
headers['Authorization'] = 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNTkwMjU5NjM1LCJqdGkiOiJkMGRmOWZjMzI1MTQ0MTU1OTM1YTRiODZlNGZjYWFkMyIsInVzZXJfaWQiOjF9.iG92hKRyolYvQJDnQmLD3t25-YrFVoPtqWWvzP8f1OQ'

r = requests.get('http://chariya.webfactional.com/genera/',headers=headers)

print(r.text)