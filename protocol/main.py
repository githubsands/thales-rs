import subprocess
import os
import shutil
import traceback
import logging
import json

CHAIN_REGISTRY_URI='https://github.com/cosmos/chain-registry'
CHAIN_REGISTRY_DIR=os.getcwd() + "/data/chain-registry-cosmos"
CHAIN_FILE="chain.json"
PROTOCOLS=os.chdir(CHAIN_REGISTRY_DIR)

class chain_manager():
    def __init__(self, file_path):
        self.file_path = file_path
        self.chains_list= []
        if os.path.exists(CHAIN_REGISTRY_DIR):
            print('chain_dir exists - not cloning from git')
        else:
            subprocess.run(['git', 'clone', CHAIN_REGISTRY_URI, clone_dir])
        self.clean_directory()
        self.create_cosmos_chains()
    def clean_directory(self):
            remove_dirs=["/.git", "/.github", "/_IBC", "/_non-cosmos"]
            remove_files=["/chain.schema.json", "/ibc_data.schema.json"]
            for remove_dir in remove_dirs:
                try:
                    shutil.rmtree(CHAIN_REGISTRY_DIR+remove_dir)
                except OSError as e:
                    continue
            for remove_file in remove_files:
                try:
                    os.remove(CHAIN_REGISTRY_DIR+remove_file)
                except OSError as e:
                    continue
    def create_cosmos_chains(self):
        self.chains_list = os.listdir(CHAIN_REGISTRY_DIR)
        self.chains = []
        for c in self.chains_list:
            try:
                chain_file = CHAIN_REGISTRY_DIR+"/"+c+"/"+CHAIN_FILE
                self.chains.append(TendermintChain(c, chain_file))
            except Exception as e:
                logging.error(traceback.format_exc())
                print("failed to add chain:"+c+"\n"+"chain_file:"+chain_file+"\n")
                continue

        print("printing chains", self.chains)

class TendermintChain:
    def __init__(self, name, chain_file_path):
        with open(chain_file_path) as f:
            data = json.load(f)

        self.name = name

        self.schema = data.get("$schema")
        self.chain_name = data.get("chain_name")
        self.website = data.get("website")
        self.status = data.get("status")
        self.network_type = data.get("network_type")
        self.pretty_name = data.get("pretty_name")
        self.chain_id = data.get("chain_id")
        self.bech32_prefix = data.get("bech32_prefix")
        self.node_home = data.get("node_home")
        self.daemon_name = data.get("daemon_name")
        self.slip44 = data.get("slip44")

        fees = data.get("fees")
        if fees:
            fee_tokens = fees.get("fee_tokens")
            if fee_tokens:
                self.fee_denom = fee_tokens[0].get("denom")
                self.fee_low_gas_price = fee_tokens[0].get("low_gas_price")
                self.fee_average_gas_price = fee_tokens[0].get("average_gas_price")
                self.fee_high_gas_price = fee_tokens[0].get("high_gas_price")

        staking = data.get("staking")
        if staking:
            staking_tokens = staking.get("staking_tokens")
            if staking_tokens:
                self.staking_denom = staking_tokens[0].get("denom")

        codebase = data.get("codebase")
        if codebase:
            self.git_repo = codebase.get("git_repo")
            self.recommended_version = codebase.get("recommended_version")
            self.compatible_versions = codebase.get("compatible_versions")
            
            genesis = codebase.get("genesis")
            if genesis:
                self.genesis_url = genesis.get("genesis_url")

        peers = data.get("peers")
        if peers:
            seeds = peers.get("seeds")
            if seeds:
                self.seed_id = seeds[0].get("id")
                self.seed_address = seeds[0].get("address")
                
            persistent_peers = peers.get("persistent_peers")
            if persistent_peers:
                self.persistent_peers = persistent_peers

        apis = data.get("apis")
        if apis:
            rpc = apis.get("rpc")
            if rpc:
                self.rpc_addresses = [x.get("address") for x in rpc]
                
            rest = apis.get("rest")
            if rest:
                self.rest_addresses = [x.get("address") for x in rest]
                
            grpc = apis.get("grpc")
            if grpc:
                self.grpc_addresses = [x.get("address") for x in grpc]

        explorers = data.get("explorers")
        if explorers:
            self.explorer_urls = [x.get("url") for x in explorers]
            self.tx_pages = [x.get("tx_page") for x in explorers]

def main():
    chains_dir=chain_manager(CHAIN_REGISTRY_DIR)

if __name__ == "__main__":
    main()
