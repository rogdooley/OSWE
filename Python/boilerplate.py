import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Description of your script.")
    
    parser.add_argument("-i", "--input", type=str, required=True, help="Input file path")
    parser.add_argument("-o", "--output", type=str, required=True, help="Output file path")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose mode")
    
    return parser.parse_args()

def main():
    args = parse_args()
    
    # Your main code logic here

if __name__ == "__main__":
    main()

