"""Ubiquitous Language - BEFORE

Tim bisnis bilang "order dibayar" dan "order dibatalkan".
Di kode yang muncul malah process(data, 2), "st", dan "amt".
Setiap kali bicara dengan tim bisnis, developer harus menerjemahkan dulu.
"""


def process(data: dict, flag: int) -> dict:
    if flag == 1:        # 1 = baru
        data["st"] = 1
    elif flag == 2:      # 2 = bayar
        if data["st"] != 1:
            raise Exception("gagal")
        data["st"] = 2
    elif flag == 3:      # 3 = batal
        if data["st"] != 1:
            raise Exception("gagal")
        data["st"] = 3
    return data


if __name__ == "__main__":
    trx = {"cust": "budi@mail.com", "amt": 200_000}
    trx = process(trx, 1)
    trx = process(trx, 2)
    print(trx)  # {'cust': ..., 'amt': ..., 'st': 2} -> 2 itu apa?
