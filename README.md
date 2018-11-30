# Blockchain
A Peer to Peer network for Blockchain
## Abstract
The purpose of this project in the first phase is to implement a P2P network where there is a root node which plays role of a DNS server and client nodes which send messages to each other to make the conncetion alive.
In the next phase we are going to to run a blockchain application on Our Network.(coming soon!)
## Inroduction
P2P stands for Peer-to-Peer is a distributed application architecture that partitions tasks or workloads between peers. Peers are equally privileged, equipotent participants in the application. They are said to form a peer-to-peer network of nodes. Torrent, Tor, Bitcoin etc. are most famous samples of P2P networks.
## Network Protocol
### Client
The fisrt step for each client is to become registered on the network by sneding a Register Request to root. 
### Root
The first role of Root is to register clients in the network by responing to their Register Request message.
## Implementation
In this section we are  going to describe role of object, their methods and
### Peer
### Stream
### Node
### Packet
### PacketFactory
### UserInterface
## UML
![uml1](https://user-images.githubusercontent.com/24544896/49306252-f4b5a300-f4e6-11e8-843e-8545596bc1ec.PNG)
![uml2](https://user-images.githubusercontent.com/24544896/49306251-f41d0c80-f4e6-11e8-9503-b518492a8c6e.PNG)
