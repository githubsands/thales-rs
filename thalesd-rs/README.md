# Thales-rs

Crosschain capital allocator between solana and ethereum blockchains. Capital is deposited
in either a solana or ethereum chain.

CheckTx
BeginBlock
DeliverTx
EndBlock



1. Problem-set

* How can we order trades by price and time in a tendermint mempool
* Is this tendermint memepool already made for us
* What is this key-value database structure that is committed and shared within blocks.
* How do we go from transaction to key value store?
* What should be within our blocks

2. Thales block

* Thales block hold TraderAccounts and funding




3. Money Manager

* Performs CheckTx when verifying funds of a trader
* Performs DeliverTx when matching to orders
*
