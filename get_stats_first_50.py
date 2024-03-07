arr = []
with open('first50_res.txt', 'r') as f:
    kek = f.read().split('\n')
    for line in kek:
        if len(line) > 1:
            arr.append(int(line[1:3]))
with open('base/first50_res.txt', 'r') as f:
    kek = f.read().split('\n')
    for line in kek:
        if len(line) > 1:
            arr.append(int(line[1:3]))
print(f'size: {len(arr)}')
cnt = [0] * 26
for i in arr:
    cnt[i] += 1
for j in range(25, -1, -1):
    if cnt[j] != 0:
        print(f'{j}: {cnt[j] / len(arr)}')
