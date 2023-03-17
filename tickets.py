DEFAULTTICKETS = 100


def get(id):
    with open('tickets.txt', 'r') as f:
        for line in f:
            arr = line.split(':')
            if arr[0] == id:
                return int(arr[1])
    with open('tickets.txt', 'w') as f:
        f.write(f'{id}:{DEFAULTTICKETS}\n')
    return DEFAULTTICKETS
