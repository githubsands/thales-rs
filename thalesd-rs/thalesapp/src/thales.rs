use std::{
    collections::HashMap,
    sync::mpsc::{channel, Receiver, Sender},
};

use crate::{codec::MAX_VARINT_LENGTH, Application, Error};
use bytes::BytesMut;
use crossbeam_channel::{select, unbounded, Receiver, Sender};
use tracing::{debug, info};

use tendermint_abci::{ClientBuilder, ServerBuilder, ThalesApp};
use tendermint_proto::abci::{
    Event, EventAttribute, RequestCheckTx, RequestDeliverTx, RequestInfo, RequestQuery,
    ResponseCheckTx, ResponseCommit, ResponseDeliverTx, ResponseInfo, ResponseQuery,
};

use abcidriver::ABCIDriver;
use orderbook::Orderbook;

fn thales() {
    let (app, wsserver, mem_pool, indexer, abci_driver) = ThalesApp::new();
    let server = ServerBuilder::default()
        .bind("127.0.0.1:26658", app)
        .unwrap();
    std::thread::spawn(move || abci_driver.run());
    std::thread::spawn(move || server.listen());
    std::thread::spawn(move || ws_server.listen());
    std::thread::spawn(move || indexer.consume());
    std::thread::spawn(move || mem_pool.start());
    let mut client = ClientBuilder::default().connect(server_addr).unwrap();
    let res = client
        .echo(RequestEcho {
            message: "Hello ABCI!".to_string(),
        })
        .unwrap();
    assert_eq!(res.message, "Hello ABCI!");
    client
        .deliver_tx(RequestDeliverTx {
            tx: "test-key=test-value".into(),
        })
        .unwrap();
    client.commit().unwrap();
    let res = client
        .query(RequestQuery {
            data: "test-key".into(),
            path: "".to_string(),
            height: 0,
            prove: false,
        })
        .unwrap();
    assert_eq!(res.value, "test-value".as_bytes().to_owned());
}

#[derive(Debug, Clone)]
pub struct ThalesApp {
    abci_driver: ABCIDriver,
    order_book: Orderbook,
    sender_chan: Sender<Command>,
    receiver_chan: <Command>,
}

impl ThalesApp {
    /// Constructor.
    pub fn new() -> (Self, ThalesDriver) {
        let (cmd_tx, cmd_rx) = channel();
        (Self { cmd_tx }, ThalesDriver::new(cmd_rx))
    }

    /// Attempt to retrieve the value associated with the given key.
    pub fn get<K: AsRef<str>>(&self, key: K) -> Result<(i64, Option<String>), Error> {
        let (result_tx, result_rx) = channel();
        channel_send(
            &self.cmd_tx,
            Command::Get {
                key: key.as_ref().to_string(),
                result_tx,
            },
        )?;
        channel_recv(&result_rx)
    }

    /// Attempt to set the value associated with the given key.
    ///
    /// Optionally returns any pre-existing value associated with the given
    /// key.
    pub fn set<K, V>(&self, key: K, value: V) -> Result<Option<String>, Error>
    where
        K: AsRef<str>,
        V: AsRef<str>,
    {
        let (result_tx, result_rx) = channel();
        channel_send(
            &self.cmd_tx,
            Command::Set {
                key: key.as_ref().to_string(),
                value: value.as_ref().to_string(),
                result_tx,
            },
        )?;
        channel_recv(&result_rx)
    }
}

impl Application for ThalesApp {
    fn info(&self, request: RequestInfo) -> ResponseInfo {
        debug!(
            "Got info request. Tendermint version: {}; Block version: {}; P2P version: {}",
            request.version, request.block_version, request.p2p_version
        );

        let (result_tx, result_rx) = channel();
        channel_send(&self.cmd_tx, Command::GetInfo { result_tx }).unwrap();
        let (last_block_height, last_block_app_hash) = channel_recv(&result_rx).unwrap();

        ResponseInfo {
            data: "kvstore-rs".to_string(),
            version: "0.1.0".to_string(),
            app_version: 1,
            last_block_height,
            last_block_app_hash: last_block_app_hash.into(),
        }
    }
    fn query(&self, request: RequestQuery) -> ResponseQuery {
        let key = match std::str::from_utf8(&request.data) {
            Ok(s) => s,
            Err(e) => panic!("Failed to intepret key as UTF-8: {e}"),
        };
        debug!("Attempting to get key: {}", key);
        match self.get(key) {
            Ok((height, value_opt)) => match value_opt {
                Some(value) => ResponseQuery {
                    code: 0,
                    log: "exists".to_string(),
                    info: "".to_string(),
                    index: 0,
                    key: request.data,
                    value: value.into_bytes().into(),
                    proof_ops: None,
                    height,
                    codespace: "".to_string(),
                },
                None => ResponseQuery {
                    code: 0,
                    log: "does not exist".to_string(),
                    info: "".to_string(),
                    index: 0,
                    key: request.data,
                    value: Default::default(),
                    proof_ops: None,
                    height,
                    codespace: "".to_string(),
                },
            },
            Err(e) => panic!("Failed to get key \"{key}\": {e:?}"),
        }
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

/// Manages key/value store state.
#[derive(Debug)]
pub struct ABIDriver {
    store: HashMap<String, String>,
    height: i64,
    app_hash: Vec<u8>,
    cmd_rx: Receiver<Command>,
}

impl ThalesTendermintHandler {
    fn new(cmd_rx: Receiver<Command>) -> Self {
        Self {
            store: HashMap::new(),
            height: 0,
            app_hash: vec![0_u8; MAX_VARINT_LENGTH],
            cmd_rx,
        }
    }
    pub fn run(mut self) -> Result<(), Error> {
        loop {
            let cmd = self.cmd_rx.recv().map_err(Error::channel_recv)?;
            match cmd {
                Command::GetInfo { result_tx } => {
                    channel_send(&result_tx, (self.height, self.app_hash.clone()))?
                }
                Command::Get { key, result_tx } => {
                    debug!("Getting value for \"{}\"", key);
                    channel_send(
                        &result_tx,
                        (self.height, self.store.get(&key).map(Clone::clone)),
                    )?;
                }
                Command::Set {
                    key,
                    value,
                    result_tx,
                } => {
                    debug!("Setting \"{}\" = \"{}\"", key, value);
                    channel_send(&result_tx, self.store.insert(key, value))?;
                }
                Command::Commit { result_tx } => self.commit(result_tx)?,
            }
        }
    }
    fn commit(&mut self, result_tx: Sender<(i64, Vec<u8>)>) -> Result<(), Error> {
        let mut app_hash = BytesMut::with_capacity(MAX_VARINT_LENGTH);
        prost::encoding::encode_varint(self.store.len() as u64, &mut app_hash);
        self.app_hash = app_hash.to_vec();
        self.height += 1;
        channel_send(&result_tx, (self.height, self.app_hash.clone()))
    }
}
