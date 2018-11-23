from src.Peer import Peer

if __name__ == "__main__":

    client = Peer("127.000.000.001", 19125, is_root=False, root_address=("127.000.000.001", 5353))

    client.start_user_interface()
    client.run()
