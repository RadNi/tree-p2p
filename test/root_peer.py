from src.Peer import Peer

if __name__ == "__main__":
    server = Peer("192.168.202.221", 5356, is_root=True)
    server.start_user_interface()

    server.run()

