import pandas_read_xml as pdx

# Đọc file XML vào DataFrame
df = pdx.read_xml("../dataset/SalesTransactions.xml", ['UelSample', 'SalesItem'])

print(df)                # In toàn bộ DataFrame
print(df.iloc[0])        # In dòng đầu tiên

data = df.iloc[0]        # Gán dòng đầu tiên cho biến data

print(data[0])           # In phần tử đầu tiên trong dòng
print(data[1])           # In phần tử thứ hai trong dòng
print(data[1]["OrderID"])# In giá trị OrderID của phần tử thứ hai
