import pandas as pd
def parse_receipt(raw_str: str):
    answer = []

    strings = raw_str.split("\n")

    date = strings[1][7:]

    for i in range(4, len(strings) - 16, 3):
        id, name = strings[i].split(". ", 1)
        id = int(id)
        cost, other = strings[i+1].split(" x ")
        cnt, price = other.split(" = ")
        cost, cnt = float(cost), float(cnt)

        answer.append((id, name, cnt, cost,date))

    return answer

f = open('data/m1.txt','r')

data = parse_receipt(f.read())
df = pd.DataFrame(data, columns =['check_id', 'name', 'amount','unit_price','date'])
print(df)

df['check_id'] = 0
df.to_csv('data/UnResolvedReceipt.csv',index=False)
print(df)

