import subprocess

CHAIN_REGISTRY_URI='https://github.com/cosmos/chain-registry'

def main():
    subprocess.run(['git', 'clone', CHAIN_REGISTRY_URI, 'chain-registry-cosmos'])
    for folder in os.listdir(directory):
        if filename.endswith('.json'):
            # Read the contents of the JSON file
            with open(os.path.join(directory, filename), 'r') as file:
                json_data = json.load(file)
            value = json_data[key]
            print(f'{filename}: {value}')
        with open('data.json', 'r'





    subprocess.run(['git', 'clone', CHAIN_REGISTRY_URI, 'chain-registry-cosmos'])

if __name__ == '__main__':
    main()
