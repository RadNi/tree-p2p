from src.Peer import Peer

if __name__ == "__main__":
    server = Peer("127.000.000.001", 5353, is_root=True)
    server.start_user_interface()

    server.run()