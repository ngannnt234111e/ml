import pandas as pd

def find_orders_with_sort(df, minValue, maxValue, SortType=True):
    # Tính tổng giá trị từng đơn hàng
    order_totals = df.groupby('OrderID').apply(
        lambda x: (x['UnitPrice'] * x['Quantity'] * (1 - x['Discount'])).sum()
    )

    # Lọc các đơn hàng trong khoảng minValue … maxValue
    orders_within_range = order_totals[(order_totals >= minValue) & (order_totals <= maxValue)]

    # Sắp xếp theo SortType
    sorted_orders = orders_within_range.sort_values(ascending=not SortType)

    # Đưa về DataFrame hiển thị OrderID và Sum
    result = pd.DataFrame({
        'OrderID': sorted_orders.index,
        'Sum': sorted_orders.values
    })

    return result

# Đọc dữ liệu
df = pd.read_csv('../dataset/SalesTransactions.csv')

# Nhập khoảng giá trị
minValue = float(input("Nhập giá trị min: "))
maxValue = float(input("Nhập giá trị max: "))

# Nhập kiểu sắp xếp (True = giảm dần, False = tăng dần)
SortType = input("Sort giảm dần? (y/n): ").lower() == 'y'

result = find_orders_with_sort(df, minValue, maxValue, SortType)

print("Danh sách các hóa đơn trong phạm vi:")
print(result)
