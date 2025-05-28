import sys

# Variables to maintain the simulation statistics
Hit = 0
Miss = 0
reads = 0
writes = 0

def update_lru(address):
    # Logic for updating LRU policy
    set_idx = (address // BLOCK_SIZE) % NUM_SETS
    tag = address // BLOCK_SIZE

    if tag in lru_position[set_idx][1]:
        lru_position[set_idx][0].remove(tag)
        lru_position[set_idx][0].append(tag)
        lru_position[set_idx][1][tag] = len(lru_position[set_idx][0]) - 1
    else:
        lru_position[set_idx][0].append(tag)
        lru_position[set_idx][1][tag] = len(lru_position[set_idx][0]) - 1

def simulate_access(op, address):
    set_idx = (address // BLOCK_SIZE) % NUM_SETS
    tag = address // BLOCK_SIZE
    found = False
    global reads, writes, Hit, Miss

    for i in range(len(tag_array[set_idx])):
        if tag == tag_array[set_idx][i]:
            found = True
            Hit += 1
            if is_lru:
                update_lru(address)
            if op == 'W' and WB:
                dirty[tag] = True
            elif op == 'W':
                writes += 1
            break

    if not found:
        Miss += 1
        if len(tag_array[set_idx]) == ASSOC:
            if is_lru:
                evicted = lru_position[set_idx][0].pop(0)
                tag_array[set_idx].remove(evicted)
                del lru_position[set_idx][1][evicted]
            elif is_fifo:
                evicted = tag_array[set_idx].pop(0)
            elif is_lifo:
                evicted = tag_array[set_idx].pop()

            if evicted in dirty:
                del dirty[evicted]
                writes += 1

        tag_array[set_idx].append(tag)

        if is_lru:
            update_lru(address)
        if op == 'W' and WB:
            dirty[tag] = True
        elif op == 'W':
            writes += 1
        reads += 1

if __name__ == "__main__":
    # ./SIM <CACHE_SIZE> <ASSOC> <REPLACEMENT> <WB> <TRACE_FILE>
    arguments = sys.argv[1:]
    CACHE_SIZE = int(arguments[0])
    ASSOC = int(arguments[1])
    if ASSOC == 0:
        print("Associativity shouldn't be 0")
        sys.exit(1)

    BLOCK_SIZE = 64
    NUM_SETS = CACHE_SIZE // (BLOCK_SIZE * ASSOC)

    is_lru = False
    is_fifo = False
    is_lifo = False

    if arguments[2] == '0':
        is_lru = True
    elif arguments[2] == '1':
        is_fifo = True
    elif arguments[2] == '2':
        is_lifo = True

    WB = bool(int(arguments[3]))

    tag_array = [[] for _ in range(NUM_SETS)]
    lru_position = [[[], {}] for _ in range(NUM_SETS)]
    dirty = {}

    with open(arguments[4], 'r') as file:
        for line in file:
            op, address = line.split()
            address = int(address, 16)
            simulate_access(op, address)

    print(f"Hits: {Hit}")
    print(f"Misses: {Miss}")
    print(f"Reads: {reads}")
    print(f"Writes: {writes}")
    print(f"Miss ratio: {Miss / (Miss + Hit):.4f}")
