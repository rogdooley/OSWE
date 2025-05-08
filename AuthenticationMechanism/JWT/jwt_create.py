import argparse
import jwt
import json

def create_jwt(secret, algorithm, payload):
    try:
        # Load JSON payload
        payload_dict = json.loads(payload)
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON payload")

    # Create JWT
    token = jwt.encode(payload_dict, secret, algorithm=algorithm)
    return token

def main():
    parser = argparse.ArgumentParser(description="Generate a JWT with a given secret, algorithm, and payload.")
    parser.add_argument("--secret", required=True, help="Signing secret key")
    parser.add_argument("--algo", required=True, choices=jwt.algorithms.get_default_algorithms().keys(), help="Signature algorithm (e.g., HS256, RS256)")
    parser.add_argument("--payload", required=True, help="JSON payload for the JWT")

    args = parser.parse_args()

    try:
        jwt_token = create_jwt(args.secret, args.algo, args.payload)
        print(f"Generated JWT: {jwt_token}")
    except ValueError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

