from src.Peer import Peer

if __name__ == "__main__":
    server = Peer("000.000.000.000", 6666, is_root=True)
    server.start_user_interface()

    server.run()