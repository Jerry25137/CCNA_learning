"""

IP Address find Network ID, Broadcast address

for IPv4

"""

import sys

# 十進位轉二進位
# 將每個十進位整數（IP位元組）轉換為8位的二進位，並平鋪成32位的list
def dec_to_bin(dec_list):
    bin_list = []
    for i in dec_list:
        X = bin(i)[2:]  # 去掉開頭的 '0b'
        
        if len(X) < 8:
            for j in range(8 - len(X)):  # 補足前綴0使其成為8位
                bin_list.append(0)
        
        for k in X:  # 將字元逐一轉成int加進list中
            bin_list.append(int(k))
        
    return bin_list

# 找 Network ID
# 將 IP 和 subnet mask 做 bitwise AND，並組合回四個十進位數字
def find_network_id(ip_bin, mask_bin):
    network_id = []
    n = 7  # 控制每8位重組一次成一個byte
    x = 0
    for i in range(len(ip_bin)):
        x += ip_bin[i] * mask_bin[i] * 2**n  # 做 bitwise AND 並還原成十進位加總

        if n > 0:
            n -= 1
        else:
            network_id.append(x)  # 每8位湊齊時存入 network_id
            n = 7
            x = 0
    
    return network_id

# 找 Broadcast Address
# 將 Network ID 的 host bits 全部補 1，得到廣播位址
def find_broadcast_address(network_id, mask_bin):
    broadcast_addr_bin = []                  # 最終的32位廣播位址二進位
    broadcast_addr = []                      # 最終的四個十進位結果
    ip_range = mask_bin.count(1)             # 網路位元數
    network_id_bin = dec_to_bin(network_id)  # 將 Network ID 轉回 32位元格式

    for i in range(len(network_id_bin)):
        if i < ip_range:
            broadcast_addr_bin.append(network_id_bin[i])  # 網路部分保留
        else:    
            broadcast_addr_bin.append(1)  # 主機部分補 1
    
    # 將32位元二進位還原成四個十進位數字
    n = 7
    x = 0
    for i in range(len(broadcast_addr_bin)):
        x += broadcast_addr_bin[i] * 2**n

        if n > 0:
            n -= 1
        else:
            broadcast_addr.append(x)
            n = 7
            x = 0
    
    return broadcast_addr

# 資料驗證
# 驗證 IP 或子網遮罩是否為合法的四個數字，範圍 0~255
def validate_ip(ip_list):
    if len(ip_list) != 4:
        return False
    
    for n in ip_list:
        if not (0 <= n <= 255):
            return False
        
    return True


# IP 加減位移
# 將四段 IP 地址轉換為整數加總 offset，再轉回四段 IP 格式
def add_ip(ip, offset):
    ip_int = ip[0] * 256 ** 3 + ip[1] * 256 ** 2 + ip[2] * 256 + ip[3] + offset
    return [
            (ip_int >> 24) & 255,
            (ip_int >> 16) & 255,
            (ip_int >> 8)  & 255,
            ip_int & 255
            ]

# 主程式進入點
if __name__ == "__main__":
    try:
        ip_address  = input("IP Address = ")  # 例："192.168.1.70"
        
        # 如果是 CIDR 格式，例如 "192.168.1.70/26"
        if "/" in ip_address:
            X = ip_address.split("/")
            ip_address_list = list(map(int, X[0].split(".")))  # 拆成 list: [192,168,1,70]
            
            if not validate_ip(ip_address_list):
                raise ValueError("IP格式不正確")
            
            # 依照 CIDR 長度建立 mask_bin，例如 /26 會產生前26個1後6個0
            mask_bin = []
            prefix_len = int(X[1])
            if prefix_len >= 0 and prefix_len <= 32:
                for i in range(32):
                    if i < prefix_len:
                        mask_bin.append(1)
                    else:
                        mask_bin.append(0)
            else:
                raise ValueError("CIDR遮罩長度必須在 0 ~ 32 之間")
        
        # 如果是 IP + 傳統子網遮罩格式
        else:
            subnet_mask = input("Subnet Mask = ")  # 例："255.255.255.192"
            ip_address_list  = list(map(int, ip_address.split(".")))
            subnet_mask_list = list(map(int, subnet_mask.split(".")))
            
            # 驗證 IP 與遮罩格式是否合法
            if not validate_ip(ip_address_list):
                raise ValueError("IP格式不正確")
                
            if not validate_ip(subnet_mask_list):
                raise ValueError("子網遮罩格式不正確")
            
            # 將遮罩轉為 32 位元的二進位 list
            mask_bin = dec_to_bin(subnet_mask_list)
        
        ip_bin         = dec_to_bin(ip_address_list)                   # IP轉為32位元格式
        network_id     = find_network_id(ip_bin, mask_bin)             # 計算Network ID
        broadcast_addr = find_broadcast_address(network_id, mask_bin)  # 計算Broadcast Address
        
        # 輸出結果（包含 CIDR 表示法）
        print(f"Network_ID = {network_id[0]}.{network_id[1]}.{network_id[2]}.{network_id[3]} /{mask_bin.count(1)}")
        print(f"Broadcast_Address = {broadcast_addr[0]}.{broadcast_addr[1]}.{broadcast_addr[2]}.{broadcast_addr[3]} /{mask_bin.count(1)}")
        
        # 計算 usable IP 範圍
        first_ip = add_ip(network_id, 1)       # 第一個可用 IP
        last_ip  = add_ip(broadcast_addr, -1)  # 最後一個可用 IP
        
        print(f"IP Range = {first_ip[0]}.{first_ip[1]}.{first_ip[2]}.{first_ip[3]} ~ {last_ip[0]}.{last_ip[1]}.{last_ip[2]}.{last_ip[3]}")
        print(f"Usable Hosts = {2**(32 - mask_bin.count(1)) - 2}")
    
    except Exception as e:
        print(f"出現錯誤：{e}")
        sys.exit(1)  # 出錯時結束程式