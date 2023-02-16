struct ABCIDriver {
    tx_receiver: Receiver,
    store: HashMap<String, String>,
    height: i64,
    app_hash: Vec<u8>,
}

impl ABCIDriver {
    pub fn new() -> Self {
        let (cmd_tx, cmd_rx) = channel();
        ABCIDriver {}
    }
    pub fn run(mut self) -> Result<(), Error> {
        loop {
            let cmd = self.tx_receiver.recv().map_err(Error::channel_recv)?;
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

// Implement `RequestDispatcher` for all `Application`s.
impl<A: Application> RequestDispatcher for A {
    fn handle(&self, request: Request) -> Response {
        tracing::debug!("Incoming request: {:?}", request);
        Response {
            value: Some(match request.value.unwrap() {
                Value::Echo(req) => response::Value::Echo(self.echo(req)),
                Value::Flush(_) => response::Value::Flush(self.flush()),
                Value::Info(req) => response::Value::Info(self.info(req)),
                Value::InitChain(req) => response::Value::InitChain(self.init_chain(req)),
                Value::Query(req) => response::Value::Query(self.query(req)),
                Value::BeginBlock(req) => response::Value::BeginBlock(self.begin_block(req)),
                Value::CheckTx(req) => response::Value::CheckTx(self.check_tx(req)),
                Value::DeliverTx(req) => response::Value::DeliverTx(self.deliver_tx(req)),
                Value::EndBlock(req) => response::Value::EndBlock(self.end_block(req)),
                Value::Commit(_) => response::Value::Commit(self.commit()),
                Value::ListSnapshots(_) => response::Value::ListSnapshots(self.list_snapshots()),
                Value::OfferSnapshot(req) => {
                    response::Value::OfferSnapshot(self.offer_snapshot(req))
                }
                Value::LoadSnapshotChunk(req) => {
                    response::Value::LoadSnapshotChunk(self.load_snapshot_chunk(req))
                }
                Value::ApplySnapshotChunk(req) => {
                    response::Value::ApplySnapshotChunk(self.apply_snapshot_chunk(req))
                }
                Value::SetOption(_) => response::Value::SetOption(Default::default()),
            }),
        }
    }
}

pub fn run(mut self) -> Result<(), Error> {
    loop {
        let cmd = self.tx_receiver.recv().map_err(Error::channel_recv)?;
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

fn channel_send<T>(tx: &Sender<T>, value: T) -> Result<(), Error> {
    tx.send(value).map_err(Error::send)
}

fn channel_recv<T>(rx: &Receiver<T>) -> Result<T, Error> {
    rx.recv().map_err(Error::channel_recv)
}
