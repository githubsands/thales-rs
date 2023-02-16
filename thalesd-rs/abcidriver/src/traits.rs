/// An ABCI application.
///
/// Applications are `Send` + `Clone` + `'static` because they are cloned for
/// each incoming connection to the ABCI [`Server`]. It is up to the
/// application developer to manage shared state between these clones of their
/// application.
///
/// [`Server`]: crate::Server
pub trait Application: Send + Clone + 'static {
    /// Echo back the same message as provided in the request.
    fn echo(&self, request: RequestEcho) -> ResponseEcho {
        ResponseEcho {
            message: request.message,
        }
    }

    /// Provide information about the ABCI application.
    fn info(&self, _request: RequestInfo) -> ResponseInfo {
        Default::default()
    }

    /// Called once upon genesis.
    fn init_chain(&self, _request: RequestInitChain) -> ResponseInitChain {
        Default::default()
    }

    /// Query the application for data at the current or past height.
    fn query(&self, _request: RequestQuery) -> ResponseQuery {
        Default::default()
    }

    /// Check the given transaction before putting it into the local mempool.
    fn check_tx(&self, _request: RequestCheckTx) -> ResponseCheckTx {
        Default::default()
    }

    /// Signals the beginning of a new block, prior to any `DeliverTx` calls.
    fn begin_block(&self, _request: RequestBeginBlock) -> ResponseBeginBlock {
        Default::default()
    }

    /// Apply a transaction to the application's state.
    fn deliver_tx(&self, _request: RequestDeliverTx) -> ResponseDeliverTx {
        Default::default()
    }

    /// Signals the end of a block.
    fn end_block(&self, _request: RequestEndBlock) -> ResponseEndBlock {
        Default::default()
    }

    /// Signals that messages queued on the client should be flushed to the server.
    fn flush(&self) -> ResponseFlush {
        ResponseFlush {}
    }

    /// Commit the current state at the current height.
    fn commit(&self) -> ResponseCommit {
        Default::default()
    }

    /// Used during state sync to discover available snapshots on peers.
    fn list_snapshots(&self) -> ResponseListSnapshots {
        Default::default()
    }

    /// Called when bootstrapping the node using state sync.
    fn offer_snapshot(&self, _request: RequestOfferSnapshot) -> ResponseOfferSnapshot {
        Default::default()
    }

    /// Used during state sync to retrieve chunks of snapshots from peers.
    fn load_snapshot_chunk(&self, _request: RequestLoadSnapshotChunk) -> ResponseLoadSnapshotChunk {
        Default::default()
    }

    /// Apply the given snapshot chunk to the application's state.
    fn apply_snapshot_chunk(
        &self,
        _request: RequestApplySnapshotChunk,
    ) -> ResponseApplySnapshotChunk {
        Default::default()
    }
}
