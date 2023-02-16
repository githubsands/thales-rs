const ASK: &str = "ASK";
const BID: &str = "BID";

pub struct Orderbook {
    side: &'static str,
    orders: Box<Vec<Order>>,
}
