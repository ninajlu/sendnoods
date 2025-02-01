import base64

CHUNK_SIZE = 48000  # GitHub has a 48KB limit per secret

def split_session_file(filename):
    with open(filename, 'rb') as f:
        data = f.read()
    
    b64_data = base64.b64encode(data).decode()
    chunks = [b64_data[i:i+CHUNK_SIZE] for i in range(0, len(b64_data), CHUNK_SIZE)]
    
    print(f"Number of chunks: {len(chunks)}")
    for i, chunk in enumerate(chunks):
        print(f"\nCHUNK_{i+1}:")
        print(chunk)

if __name__ == "__main__":
    split_session_file('session.session') 