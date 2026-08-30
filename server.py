import socket
import threading
import time

mock_services = {
    "docker": "Running (5 containers)",
    "plex": "Running (1 active stream)",
    "jellyfin": "Stopped",
    "pihole": "Running (Blocking 15.4%)",
    "nas": "Online (Free: 2.1TB)"
}

def handle_client(conn, addr):
    thread_name = threading.current_thread().name
    print(f"[+] Connection accepted from {addr} on {thread_name}")
    
    conn.sendall(b"220 HSTP_SERVER_READY\n")
    
    while True:
        try:
            data = conn.recv(1024).decode('utf-8').strip()
            if not data:
                break
                
            print(f"[RECV] {thread_name} ({addr[0]}): {data}")
            
            parts = data.split(" ", 1)
            command = parts[0]
            args = parts[1] if len(parts) > 1 else ""
            
            response = ""
            if command == "REQ_SYS":
                response = "200 OK_STATUS CPU:12%|RAM:4GB/16GB\n"
                
            elif command == "REQ_SVC":
                svc = args.lower()
                if svc in mock_services:
                    response = f"200 OK_STATUS {svc.upper()}:{mock_services[svc]}\n"
                else:
                    response = f"404 NOT_FOUND Service '{svc}' unknown\n"
                    
            elif command == "CMD_RESTART":
                svc = args.lower()
                if svc in mock_services:
                    response = f"202 ACCEPTED Restarting {svc.upper()}...\n"
                else:
                    response = "404 NOT_FOUND Cannot restart unknown service\n"
                    
            elif command == "EXIT":
                response = "200 OK_BYE\n"
                conn.sendall(response.encode('utf-8'))
                break
                
            else:
                response = "400 BAD_REQUEST Command not supported\n"
            
            print(f"[SEND] {thread_name} -> {response.strip()}")
            conn.sendall(response.encode('utf-8'))
            
        except Exception as e:
            print(f"[-] Error on {thread_name}: {e}")
            break
            
    conn.close()
    print(f"[-] Connection closed for {addr}")

def start_server(host='0.0.0.0', port=8080):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    server.settimeout(1.0)
    print(f"[*] HSTP Server listening on {host}:{port}...")
    
    try:
        while True:
            try:
                conn, addr = server.accept()
                client_thread = threading.Thread(target=handle_client, args=(conn, addr))
                client_thread.daemon = True
                client_thread.start()
            except socket.timeout:
                pass
    except KeyboardInterrupt:
        print("\n[*] Server shutting down.")
        server.close()
if __name__ == "__main__":
    start_server()