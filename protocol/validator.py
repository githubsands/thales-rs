class Validator:
    def __init__(self, validator_data):
        self.operator_address = validator_data["operator_address"]
        self.consensus_pubkey = validator_data["consensus_pubkey"]
        self.jailed = validator_data.get("jailed", False)
        self.status = validator_data.get("status", 0)
        self.tokens = validator_data.get("tokens", 0)
        self.delegator_shares = validator_data.get("delegator_shares", 0)
        self.description = validator_data.get("description", {})
        self.unbonding_height = validator_data.get("unbonding_height", 0)
        self.unbonding_time = validator_data.get("unbonding_time", "")
        self.commission = validator_data.get("commission", {})
        self.min_self_delegation = validator_data.get("min_self_delegation", "")
