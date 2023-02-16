import json

class TendermintChain:
    def __init__(self, genesis_file_path):
        with open(genesis_file_path) as f:
            self.genesis_data = json.load(f)

        # Basic Chain Parameters
        self.chain_id = self.genesis_data["chain_id"]
        self.initial_height = self.genesis_data["initial_height"]
        self.genesis_time = self.genesis_data["genesis_time"]
        self.consensus_params = self.genesis_data["consensus_params"]
        self.validators = self.genesis_data["validators"]
        self.app_hash = self.genesis_data.get("app_hash", "")
        self.app_state = self.genesis_data.get("app_state", {})

        # Account State Parameters
        self.accounts = self.app_state.get("accounts", {})

        # Staking Parameters
        self.staking = self.app_state.get("staking", {})
        self.unbonding_delegations = self.staking.get("unbonding_delegations", [])
        self.delegations = self.staking.get("delegations", [])
        self.validators_info = self.staking.get("validators", [])
        self.pool = self.staking.get("pool", {})

        # Governance Parameters
        self.gov = self.app_state.get("gov", {})
        self.deposit_params = self.gov.get("deposit_params", {})
        self.tally_params = self.gov.get("tally_params", {})
        self.voting_params = self.gov.get("voting_params", {})
        self.proposals = self.gov.get("proposals", [])

        # Slashing Parameters
        self.slashing = self.app_state.get("slashing", {})
        self.signing_infos = self.slashing.get("signing_infos", [])
        self.missed_blocks = self.slashing.get("missed_blocks", [])

        # Minting Parameters
        self.mint = self.app_state.get("mint", {})
        self.minter = self.mint.get("minter", {})
        self.params = self.mint.get("params", {})

        # Distribution Parameters
        self.distribution = self.app_state.get("distribution", {})
        self.community_tax = self.distribution.get("community_tax", "")
        self.fee_pool = self.distribution.get("fee_pool", {})
        self.delegator_withdraw_infos = self.distribution.get("delegator_withdraw_infos", {})
        self.previous_proposer = self.distribution.get("previous_proposer", "")
        self.outstanding_rewards = self.distribution.get("outstanding_rewards", {})
        self.validator_accumulated_commissions = self.distribution.get("validator_accumulated_commissions", {})
        self.validator_current_rewards = self.distribution.get("validator_current_rewards", {})
        self.validator_historical_rewards = self.distribution.get("validator_historical_rewards", {})
        self.validator_slash_events = self.distribution.get("validator_slash_events", {})
