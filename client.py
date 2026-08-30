import socket
import time

def run_client(host='127.0.0.1', port=8080):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client.connect((host, port))
        
        welcome_msg = client.recv(1024).decode('utf-8').strip()
        print(f"[SERVER]: {welcome_msg}\n")
        
        test_commands = [
            "REQ_SYS",
            "REQ_SVC plex",
            "REQ_SVC pihole",
            "REQ_SVC apache",
            "CMD_RESTART docker",
            "INVALID_COMMAND",
            "EXIT"
        ]
        
        for cmd in test_commands:
            print("-" * 40)
            print(f"Sending: {cmd}")
            client.sendall((cmd + "\n").encode('utf-8'))
            
            response = client.recv(1024).decode('utf-8').strip()
            
            parts = response.split(" ", 2)
            status_code = parts[0]
            status_phrase = parts[1] if len(parts) > 1 else ""
            data = parts[2] if len(parts) > 2 else ""
            
            print(f"Raw Response: {response}")
            print(f">> Parsed - Code: {status_code}, Phrase: {status_phrase}, Data: {data}")
            time.sleep(1)
            
    except ConnectionRefusedError:
        print("[-] Cannot connect to server. Is it running?")
    finally:
        client.close()
        print("\n[*] Client disconnected.")

if __name__ == "__main__":
    run_client()