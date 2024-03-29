use std::{env, io::Error};

use futures_util::{future, StreamExt, TryStreamExt};
use log::info;
use tokio::net::{TcpListener, TcpStream};

struct WSServer {
    address: Option<&str>,
    ws_socket: Option<TcpListener>,
}

impl WSServer {
    fn new() {
        WSServer {
            address: "127.0.0.1:8080",
        }
    }
    async fn listen(&self) {
        let try_socket = TcpListener::bind(&self.address).await;
        let listener = try_socket.expect("Failed to bind");
        info!("Listening on: {}", addr);
        while let Ok((stream, _)) = listener.accept().await {
            tokio::spawn(accept_connection(stream));
        }
        Ok(())
    }
    async fn accept_connection(stream: TcpStream) {
        let addr = stream
            .peer_addr()
            .expect("connected streams should have a peer address");
        info!("Peer address: {}", addr);

        let ws_stream = tokio_tungstenite::accept_async(stream)
            .await
            .expect("Error during the websocket handshake occurred");

        info!("New WebSocket connection: {}", addr);

        let (write, read) = ws_stream.split();
        // We should not forward messages other than text or binary.
        read.try_filter(|msg| future::ready(msg.is_text() || msg.is_binary()))
            .forward(write)
            .await
            .expect("Failed to forward messages")
    }
}
