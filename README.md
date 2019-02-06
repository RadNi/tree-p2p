## A Simple Peer To Peer Network Implementation


This project aims to implement a P2P network with the specific properties below:

* There is a Root node which acts as a DNS Server.
* Nodes connect together through messages they sent.
* User-to-network connection is done through a user interface.

To test this network, you need to be able to run both in the role (server DNS (root) and in the role of the client, and see the role and way of rejecting messages and various operations performed on the network).

### What is a P2P network

Peer-to-peer (P2P) computing or networking is a distributed application architecture that partitions tasks or workloads between peers. Peers are equally privileged, equipotent participants in the application. They are said to form a peer-to-peer network of nodes.

### Implementation

#### Peer

In this project, any Node in the network is Peer; whether it is a client or root. In other words, the deployed network is actually a combination of several peers that are connected in some way (the network graph is connected).

#### Stream

#### Node

#### Packet

#### PacketFactory

#### UserInterface


