# ip_calc_app.py

import streamlit as st

# 十進位轉二進位（例如 192.168.1.1 -> [1,1,0,0,0,0...共32位]）
def dec_to_bin(dec_list):
    bin_list = []
    for i in dec_list:
        X = bin(i)[2:]
        bin_list.extend([0] * (8 - len(X)))
        bin_list.extend([int(k) for k in X])
    return bin_list

# bitwise AND 計算 Network ID
def find_network_id(ip_bin, mask_bin):
    network_id = []
    n, x = 7, 0
    for i in range(len(ip_bin)):
        x += ip_bin[i] * mask_bin[i] * 2**n
        n -= 1
        if n < 0:
            network_id.append(x)
            n, x = 7, 0
    return network_id

# 計算 Broadcast Address
def find_broadcast_address(network_id, mask_bin):
    ip_range = mask_bin.count(1)
    network_id_bin = dec_to_bin(network_id)
    broadcast_bin = [
        network_id_bin[i] if i < ip_range else 1
        for i in range(32)
    ]

    broadcast_addr = []
    n, x = 7, 0
    for bit in broadcast_bin:
        x += bit * 2**n
        n -= 1
        if n < 0:
            broadcast_addr.append(x)
            n, x = 7, 0
    return broadcast_addr

# 驗證 IP 格式
def validate_ip(ip_list):
    return len(ip_list) == 4 and all(0 <= n <= 255 for n in ip_list)

# IP 加減（支援範圍推進）
def add_ip(ip, offset):
    ip_int = ip[0]*256**3 + ip[1]*256**2 + ip[2]*256 + ip[3] + offset
    return [
        (ip_int >> 24) & 255,
        (ip_int >> 16) & 255,
        (ip_int >> 8) & 255,
        ip_int & 255
    ]

# ---------------------------
# Streamlit App 開始
# ---------------------------

st.title("🌐 IP 網段資訊計算器")

ip_input = st.text_input("請輸入 IP（支援 CIDR 或遮罩格式）", "192.168.1.1/24")

# 當使用非CIDR格式才需要輸入遮罩
subnet_mask = ""
if "/" not in ip_input:
    subnet_mask = st.text_input("請輸入 Subnet Mask", "255.255.255.0")

if st.button("開始計算"):
    try:
        if "/" in ip_input:
            ip_part, prefix = ip_input.split("/")
            ip_address_list = list(map(int, ip_part.split(".")))
            prefix_len = int(prefix)

            if not validate_ip(ip_address_list):
                raise ValueError("IP 格式不正確")
            if not (0 <= prefix_len <= 32):
                raise ValueError("CIDR 長度需在 0 ~ 32 之間")

            mask_bin = [1 if i < prefix_len else 0 for i in range(32)]

        else:
            ip_address_list = list(map(int, ip_input.split(".")))
            subnet_mask_list = list(map(int, subnet_mask.split(".")))

            if not validate_ip(ip_address_list):
                raise ValueError("IP 格式不正確")
            if not validate_ip(subnet_mask_list):
                raise ValueError("子網遮罩格式不正確")

            mask_bin = dec_to_bin(subnet_mask_list)

        ip_bin         = dec_to_bin(ip_address_list)
        network_id     = find_network_id(ip_bin, mask_bin)
        broadcast_addr = find_broadcast_address(network_id, mask_bin)
        first_ip       = add_ip(network_id, 1)
        last_ip        = add_ip(broadcast_addr, -1)
        usable_hosts   = 2**(32 - mask_bin.count(1)) - 2

        st.success("✅ 計算結果如下：")
        st.code(f"Network ID       = {'.'.join(map(str, network_id))} /{mask_bin.count(1)}")
        st.code(f"Broadcast Address = {'.'.join(map(str, broadcast_addr))} /{mask_bin.count(1)}")
        st.code(f"Usable IP Range  = {'.'.join(map(str, first_ip))} ~ {'.'.join(map(str, last_ip))}")
        st.code(f"Usable Hosts     = {usable_hosts}")

    except Exception as e:
        st.error(f"❌ 錯誤：{e}")
