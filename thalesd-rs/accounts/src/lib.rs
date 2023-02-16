use tendermint::{PublicKey}

struct Agents {
    trader_accounts: TraderAccounts,
    thales_validators: Validators,
}

struct TradersAccounts {
    traders: HashMap<PublicKey, Account>,
}

// accounts need to be on chain
struct AccountChain {
    user: &str,
    signer: PublicKey,
    coins: HashMap<String,i64>,
}

struct AccountOffChain {
    user: &str,
    signer: PublicKey,
    orders: Box<Orders>,
}

impl Account {
    fn new(signer: PublicKey) {
    Account {
        signer: signer
        coins: HashMap::new(),
    }
}

impl account {
    fn increase(&self, coin: String, amount: i64) {
        let balance = self.coins.get(coin)
        self.coins.update(coin, balance+amount)
    }
    fn decrease(&self, coin: amount: i64) {
        let orignal = self.coins.get(coin)
        self.coins.update(coin, balance+amount)
    }
}


struct MoneyManager {
    TraderAccounts
}

impl MoneyManager {
    fn check_cash(&self, Account) {



    }

    fn check_tx(&self, _request: RequestCheckTx) -> ResponseCheckTx {
        ResponseCheckTx {
            code: 0,
            data: Default::default(),
            log: "".to_string(),
            info: "".to_string(),
            gas_wanted: 1,
            gas_used: 0,
            events: vec![],
            codespace: "".to_string(),
            ..Default::default()
        }
    }
    fn deliver_tx(&self, request: RequestDeliverTx) -> ResponseDeliverTx {
        let tx = std::str::from_utf8(&request.tx).unwrap();
        let tx_parts = tx.split('=').collect::<Vec<&str>>();
        let (key, value) = if tx_parts.len() == 2 {
            (tx_parts[0], tx_parts[1])
        } else {
            (tx, tx)
        };
        let _ = self.set(key, value).unwrap();
        ResponseDeliverTx {
            code: 0,
            data: Default::default(),
            log: "".to_string(),
            info: "".to_string(),
            gas_wanted: 0,
            gas_used: 0,
            events: vec![Event {
                r#type: "app".to_string(),
                attributes: vec![
                    EventAttribute {
                        key: "key".to_string().into_bytes().into(),
                        value: key.to_string().into_bytes().into(),
                        index: true,
                    },
                    EventAttribute {
                        key: "index_key".to_string().into_bytes().into(),
                        value: "index is working".to_string().into_bytes().into(),
                        index: true,
                    },
                    EventAttribute {
                        key: "noindex_key".to_string().into_bytes().into(),
                        value: "index is working".to_string().into_bytes().into(),
                        index: false,
                    },
                ],
            }],
            codespace: "".to_string(),
        }
    }
    fn commit(&self) -> ResponseCommit {
        let (result_tx, result_rx) = channel();
        channel_send(&self.cmd_tx, Command::Commit { result_tx }).unwrap();
        let (height, app_hash) = channel_recv(&result_rx).unwrap();
        info!("Committed height {}", height);
        ResponseCommit {
            data: app_hash.into(),
            retain_height: height - 1,
        }
    }
}

fn channel_send<T>(tx: &Sender<T>, value: T) -> Result<(), Error> {
    tx.send(value).map_err(Error::send)
}

fn channel_recv<T>(rx: &Receiver<T>) -> Result<T, Error> {
    rx.recv().map_err(Error::channel_recv)
}
