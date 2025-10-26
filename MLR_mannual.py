import numpy as np

# Data
X = np.array([
    [1, 7, 5],
    [1, 3, 7],
    [1, 5, 8],
    [1, 8, 1],
    [1, 9, 3],
    [1, 5, 4],
    [1, 4, 0],
    [1, 2, 6],
    [1, 8, 7],
    [1, 6, 4],
    [1, 9, 2]
])
y = np.array([[65], [38], [51], [38], [55], [43], [25], [33], [71], [51], [49]])

# (X'X)
XTX = X.T @ X
# (X'X)^-1
XTX_inv = np.linalg.inv(XTX)
# (X'Y)
XTY = X.T @ y
# B_hat = (X'X)^-1 * (X'Y)
B_hat = XTX_inv @ XTY

# Predicted values
y_pred = X @ B_hat

# Evaluation
mse = np.mean((y - y_pred) ** 2)
rmse = np.sqrt(mse)

# Display
print("B_hat (coefficients):")
print(B_hat)
print("\nPredicted y values:")
print(y_pred)
print("\nMSE =", mse)
print("RMSE =", rmse)
