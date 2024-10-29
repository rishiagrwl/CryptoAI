import yaml
import json
from custom_logging import crypto_logger

# Function to read JSON file
def read_json(input_file: str) -> dict:
    try:
        with open(input_file, 'r') as file:
            data = json.load(file)  # Load JSON data from the file
        crypto_logger.info(f"Successfully read JSON file: {input_file}")
        return data
    except FileNotFoundError:
        crypto_logger.error(f"File {input_file} not found.")
    except json.JSONDecodeError:
        crypto_logger.error(f"Error decoding JSON from file {input_file}.")
    except Exception as e:
        crypto_logger.error(f"An error occurred: {e}")

# Function to write data to a JSON file
def write_json(data: dict, output_file: str):
    try:
        with open(output_file, 'w') as file:
            json.dump(data, file, indent=4)  # Write data with pretty print (indent=4)
        crypto_logger.info(f"Successfully wrote JSON to file: {output_file}")
    except Exception as e:
        crypto_logger.error(f"An error occurred while writing to file {output_file}: {e}")

# Function to read YAML file
def read_yaml(input_file: str = 'config.yaml') -> dict:
    try:
        with open(input_file, 'r') as file:
            data = yaml.safe_load(file)  # Load YAML data from the file
        crypto_logger.info(f"Successfully read YAML file: {input_file}")
        return data
    except FileNotFoundError:
        crypto_logger.error(f"File {input_file} not found.")
    except yaml.YAMLError:
        crypto_logger.error(f"Error decoding YAML from file {input_file}.")
    except Exception as e:
        crypto_logger.error(f"An error occurred: {e}")

# Function to write data to a YAML file
def write_yaml(data: dict, output_file: str = 'config.yaml'):
    try:
        with open(output_file, 'w') as file:
            yaml.safe_dump(data, file, default_flow_style=False, sort_keys=False)  # Write YAML data
        crypto_logger.info(f"Successfully wrote YAML to file: {output_file}")
    except Exception as e:
        crypto_logger.error(f"An error occurred while writing to file {output_file}: {e}")
