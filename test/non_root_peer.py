from src.Peer import Peer

if __name__ == "__main__":
    client = Peer("127.000.000.001", 12220, is_root=False, root_address=("000.000.000.000", 5353))

    client.start_user_interface()
    client.run()
