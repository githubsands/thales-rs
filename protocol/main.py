import subprocess
import os
import shutil
import traceback
import logging
import json
import pandas as pd
import shutil
import urllib.request
import sys
import argparse

DATA_REGISTRY=os.getcwd() + "/data"

CHAIN_REGISTRY_URI='https://github.com/cosmos/chain-registry'
CHAIN_REGISTRY_DIR=os.getcwd() + "/data/chain-registry-cosmos"
CHAIN_TESTNET_REGISTRY_DIR=os.getcwd() + "/data/chain-registry-cosmos-testnet"
CHAIN_GENESIS_DIR=os.getcwd() + "/data/genesis/"

DATA_EXPORT=os.getcwd() + "/data/export"

CHAIN_FILE="chain.json"
GENESIS_FILE="genesis.json"

GENESIS_FOLDER_ZIP_OUTPUT=os.getcwd() + "/data/export/chain-registry.zip"
CHAINREGISTRY_FOLDER_ZIP_OUTPUT=os.getcwd() + "/data/export/chain-genesises.zip"

# TODO: Add testnets to the dataset
GENESIS_TESTNET_FOLDER_ZIP_OUTPUT=os.getcwd() + "/data/export/chain-registry-testnets.zip"
CHAINREGISTRY_FOLDER_ZIP_OUTPUT=os.getcwd() + "/data/export/chain-genesis-testnets.zip"

GRAB_GENESIS_HTTPCLIENT_TIMEOUT=3

# TODO: Add other chains to the dataset
OTHER_CHAINS= {
    "bor": ["https://github.com/maticnetwork/launch/blob/master/mainnet-v1/sentry/sentry/bor/genesis.json"],
    "hemidall": ["https://github.com/maticnetwork/launch/blob/master/mainnet-v1/sentry/sentry/heimdall/config/genesis.json"]
}

def zip_data_folder(input_folder, output_folder):
    with gzip.open(output_folder, 'wb') as f_out:
        with shutil.archive(input_folder, format='zip', root_dir='') as f_in:
            f_out.write(f_in.read())

# TODO: get a matic and others report - genesis.jsons that arn't included from our node tree
class ChainManager():
    def __init__(self, file_path):
        self.file_path = file_path
        self.chains_list = []
        self.genesis_grab_report = {}
        self.genesis_data = {}
        self.genesis_data["name"] = []
        self.genesis_data["uri"] = []
        self.genesis_data["true/false"] = []
        self.genesis_data_report = {}
        self.genesis_data_report["chain"] = []
        self.genesis_data_report["uri"] = []
        self.genesis_data_report["success"] = []
        self.genesis_data_report["error"] = []
        self.chains_list_testnet = []
        try:
            subprocess.run(['git', 'clone', CHAIN_REGISTRY_URI, CHAIN_REGISTRY_DIR])
            self.clean_directory()
            self.create_cosmos_chains()
        except Exception as e:
            logging.error(str(e))
    def clean_directory(self):
            logging.info("Cleaning registry directory")
            remove_dirs=["/.git", "/.github", "/_IBC", "/_non-cosmos"]
            remove_dirs_testnet=["/_IBC", "/_non-cosmos"]
            remove_files=["/.gitignore", "/README.md", "/chain.schema.json", "/ibc_data.schema.json", "/assetlist.schema.json"]
            shutil.move(CHAIN_REGISTRY_DIR+"/testnets", DATA_REGISTRY)
            os.rename(DATA_REGISTRY+"/testnets", CHAIN_TESTNET_REGISTRY_DIR)
            logging.info("Testnet directory created: " + CHAIN_TESTNET_REGISTRY_DIR)
            for remove_file in remove_files:
                try:
                    logging.info("Removing file" + CHAIN_REGISTRY_DIR+remove_file)
                    os.remove(CHAIN_REGISTRY_DIR+remove_file)
                except OSError as e:
                    logging.error("Failed to remove file: " + CHAIN_REGISTRY_DIR + remove_file)
                    continue
                finally:
                    logging.info("Removed file: " + CHAIN_REGISTRY_DIR + remove_file)
                    continue
            for directory in remove_dirs:
                try:
                    shutil.rmtree(CHAIN_REGISTRY_DIR+directory)
                except OSError as e:
                    logging.error("Failed to remove directory: " + CHAIN_REGISTRY_DIR + directory)
                    continue
                finally:
                    logging.info("Removed directory: " + CHAIN_REGISTRY_DIR + directory)
                    continue
            for directory in remove_dirs_testnet:
                try:
                    shutil.rmtree(CHAIN_TESTNET_REGISTRY_DIR+directory)
                except OSError as e:
                    logging.error("Failed to remove directory:" + CHAIN_TESTNET_REGISRY_DIR + remove_directory)
                    continue
                finally:
                    logging.info("Removed directory: " + CHAIN_TESTNET_REGISTRY_DIR + remove_file)
                    continue
    def create_cosmos_chains(self):
        logging.info("Creating cosmos chains")
        self.chains_list = os.listdir(CHAIN_REGISTRY_DIR)
        self.chain_list_testnet = os.listdir(CHAIN_TESTNET_REGISTRY_DIR)
        self.chains = []
        for c in self.chains_list:
            try:
                chain_file = CHAIN_REGISTRY_DIR+"/"+c+"/"+CHAIN_FILE
                logging.info("Adding cosmos chain " + chain_file)
                self.chains.append(TendermintChain(c, chain_file))
            except Exception as e:
                logging.error("Failed to add chain: "+c+"\n"+"chain_file: "+chain_file+"\n")
                continue
        for c in self.chains_list_testnet:
            try:
                chain_file = CHAIN_TESTNET_REGISTRY_DIR+"/"+c+"/"+CHAIN_FILE
                logging.info("Adding testnet cosmos chain " + chain_file)
                self.chains.append(TendermintChain(c, chain_file))
            except Exception as e:
                logging.error("Failed to add chain: "+c+"\n"+"chain_file: "+chain_file+"\n")
                continue
        for chain in self.chains:
            chain.add_genesis(self.append_genesis_report, "false")
    def print_genesis_data(self):
        for chain in self.chains:
            if hasattr(chain, "genesis_url"):
                print(chain.genesis_url)
    def export_genesis_data(self):
        df = pd.DataFrame.from_dict(self.genesis_data, orient='index')
        df.to_csv('/data/export/genesis-uri-results.csv')
    def append_genesis_report(self, name, uri, success, status):
        try:
            self.genesis_data_report["chain"].append(name)
            self.genesis_data_report["uri"].append(uri)
            self.genesis_data_report["success"].append(success)
            self.genesis_data_report["error"].append(status)
        except Exception as e:
            logging.error("failed to add append genesis report for " + name + "do to error: " + e(str))
    def export_genesis_report(self):
        """
            export_genesis_report exports the status of the data extraction for all genesis           files included in the genesis download in /data/export/genesis_report.csv
        """
        try:
            df = pd.DataFrame(self.genesis_data_report)
            df.to_csv(DATA_EXPORT+"/genesis_report.csv")
        except Exception as e:
            logging.error(e)
        finally:
            logging.info("Succesfully saved genesis data")
    def export_genesis_final(self):
        try:
            df = pd.DataFrame(self.genesis_data_report, orient='index')
            df.to_csv('/data/export/genesis-all.csv')
        except Exception as e:
            logging.error("Failed to add genesis data: "+ e(str))
        finally:
            logging.info("Successfully saved genesis data")
    def export_genesis_parameters(self):
        files = os.listdir(CHAIN_GENESIS_DIR)
        dataframes = []
        for genesis in files:
            try:
                # TODO: Fix bug here. this file(s) causes the program to hang indefinitly
                if genesis == "bluzellegenesis.json" or genesis == "starnamegenesis.json" or genesis == "regengenesis.json" or genesis == "konstellationgenesis.json" or genesis == "fetchhubgenesis.json" or genesis == "cheqdgenesis.json" or genesis == "agoricgenesis.json" or genesis == "bitcannagenesis.json" or genesis == "quicksilvergenesis.json" or genesis == "echelongenesis.json" or genesis == "diggenesis.json":
                    continue
                with open(CHAIN_GENESIS_DIR+genesis) as f:
                    data = json.load(f)
                    logging.info("loading genesis: " + CHAIN_GENESIS_DIR+genesis)
                    dataframes.append(pd.json_normalize(data))
            except Exception as e:
                logging.error("Failed to add genesis data for: " + genesis + str(e))
                timer.cancel()
                continue
        total_dataframe = pd.concat(dataframes, axis=0, ignore_index=True)
        logging.info("expoorting chains_genesis.csv to: ", DATA_EXPORT+"/chain_genesis.csv")
        total_dataframe.to_csv(DATA_EXPORT+"/chains_genesis.csv")

class TendermintChain:
    def __init__(self, name, chain_file_path):
        try:
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
                self.genesis_data = {}
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
        except Exception as e:
                logging.error(traceback.format_exc())
    def add_genesis(self, append_genesis_report_func, testnet):
        try:
            logging.info("Downloading genesis file "+self.name+" at "+self.genesis_url)
            response = {}
            self.genesis_data = {}

            # TODO: fix terra
            if self.name == "terra":
                return
            logging.log(msg="downloading genesis file " + self.genesis_url,level=1)
            response = urllib.request.urlopen(self.genesis_url, timeout=GRAB_GENESIS_HTTPCLIENT_TIMEOUT)
            self.genesis_data = json.loads(response.read())
        except urllib.error.HTTPError as e:
            append_genesis_report_func(self.name, self.genesis_url, "false", str(e))
            logging.error("failed to grab genesis due to error: "+str(e))
        except urllib.error.URLError as e:
            append_genesis_report_func(self.name, self.genesis_url, "false", str(e))
            logging.error("failed to grab genesis due to error: "+str(e))
        except Exception as e:
            append_genesis_report_func(self.name, self.genesis_url, "false", str(e))
            logging.error("failed to grab genesis due to error: "+str(e))
        finally:
            self.save_genesis(self.genesis_data, CHAIN_GENESIS_DIR+"/"+self.name+"genesis.json")
            append_genesis_report_func(self.name, self.genesis_url, "true", "NaN")
            logging.info("Successfully added genesis for "+self.name)
    def save_genesis(self, data, genesis_file_path):
            if os.path.isfile(genesis_file_path):
                print("The genesis for file "+self.name+". Using existing genesis file.")
            else:
                with open(genesis_file_path, "w") as file:
                    logging.info("Creating new genesis file for "+self.name)
                    json.dump(data, file, indent=4)
                    logging.info("Created new genesis file for "+self.name)

class Genesis:
    def __init__(self, genesis_path):
        self.genesis_path = genesis_path
        with open(genesis_path) as f:
            genesis_dict = json.load(f)
            self.genesis_time = genesis_dict.get("genesis_time")
            self.chain_id = genesis_dict.get("chain_id")
            self.consensus_params = genesis_dict.get("consensus_params")
            self.validators = genesis_dict.get("validators")
            self.app_hash = genesis_dict.get("app_hash")
            self.app_state = genesis_dict.get("app_state")
            self.genutil = genesis_dict.get("genutil")
            self.staking = genesis_dict.get("staking")
            self.gov = genesis_dict.get("gov")
            self.crisis = genesis_dict.get("crisis")
            self.slashing = genesis_dict.get("slashing")
            self.mint = genesis_dict.get("mint")
            self.distr = genesis_dict.get("distr")
            self.params = genesis_dict.get("params")
            self.evidence = genesis_dict.get("evidence")
            self.auth = genesis_dict.get("auth")
    def to_dict(self):
        return {
            "genesis_time": self.genesis_time,
            "chain_id": self.chain_id,
            "consensus_params": self.consensus_params,
            "validators": self.validators,
            "app_hash": self.app_hash,
            "app_state": self.app_state,
            "genutil": self.genutil,
            "staking": self.staking,
            "gov": self.gov,
            "crisis": self.crisis,
            "slashing": self.slashing,
            "mint": self.mint,
            "distr": self.distr,
            "params": self.params,
            "evidence": self.evidence,
            "auth": self.auth,
        }
    def load_dataframe(self):
        with open(genesis_path) as f:
            self.dataframe = pd.read_json(self.genesis_path)

# TODO: Make observer's filepath agnostic 
class Observer:
    def __init__(self):
        data = []
        self.dataframe = pd.DataFrame(data)
    def observe(self, file_path):
        try:
            with open(CHAIN_GENESIS_DIR+"/"+file_path+"genesis"+".json") as f:
                self.dataframe = pd.read_json(CHAIN_GENESIS_DIR+"/"+file_path+"genesis"+".json")
        except Exception as e:
            logging.error("Cannot print genesis: " + str(e))
        finally:
            pd.set_option('display.max_rows', None)
            pd.set_option('display.max_columns', None)
            print(self.dataframe.head())

class ObserverGenesis(Observer):
    def __init__(self):
        data = []
        self.dataframe = pd.DataFrame(data)

class ObserverChain(Observer):
    def __init__(self):
        data = []
        self.dataframe = pd.DataFrame(data)

def main():
    logging.basicConfig(
        stream=sys.stdout,
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)s %(message)s'
    )

    parser = argparse.ArgumentParser(description="Data engineering and analysis on tendermint chains")
    parser.add_argument('-r', '--reset', action='store_true', help='Removes all data')
    parser.add_argument('-pg', '--print_genesis', type=str, required=False, help='print genesis')
    parser.add_argument('-pc', '--print_chain', type=str, required=False, help='print chain')
    parser.add_argument('-gr', '--genesis_report', action='store_true', help='creates new genesis report')
    parser.add_argument('-gp', '--genesis_parameters_export', action='store_true', help='export all chain genesis parameters to a csv')
    args = parser.parse_args()

    if args.reset:
        logging.info("Removing "+ CHAIN_REGISTRY_DIR + " and " + CHAIN_GENESIS_DIR)
        shutil.rmtree(CHAIN_REGISTRY_DIR)
        shutil.rmtree(CHAIN_GENESIS_DIR)
        shutil.rmtree(CHAIN_TESTNET_REGISTRY_DIR)

    if args.print_genesis:
        logging.info("Printing genesis for " + args.print_genesis)
        observer_genesis = ObserverGenesis()
        observer_genesis.observe(args.print_genesis)

    if args.print_chain:
        logging.info("Printing genesis for " + args.print_chain)
        observer_genesis = ObserverChain()
        observer_genesis.observe(args.print_chain)

    if os.path.isdir(CHAIN_GENESIS_DIR) == False:
        os.makedirs(CHAIN_GENESIS_DIR, exist_ok=True)

    if os.path.isdir(CHAIN_REGISTRY_DIR) == False:
        os.makedirs(CHAIN_REGISTRY_DIR)

    if os.path.isdir(DATA_EXPORT) == False:
        os.makedirs(DATA_EXPORT)

    if args.genesis_report:
        logging.info("Running genesis report")
        PROTOCOLS=os.chdir(CHAIN_REGISTRY_DIR)
        chain_manager = ChainManager(CHAIN_REGISTRY_DIR)
        chain_manager.export_genesis_report()

    if args.genesis_parameters_export:
        logging.info("Running chain genesis_paramters_export")
        PROTOCOLS=os.chdir(CHAIN_REGISTRY_DIR)
        chain_manager = ChainManager(CHAIN_REGISTRY_DIR)
        chain_manager.export_genesis_parameters()

if __name__ == "__main__":
    main()
