import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

# Data
X = np.array([
    [7, 5],
    [3, 7],
    [5, 8],
    [8, 1],
    [9, 3],
    [5, 4],
    [4, 0],
    [2, 6],
    [8, 7],
    [6, 4],
    [9, 2]
])
y = np.array([65, 38, 51, 38, 55, 43, 25, 33, 71, 51, 49])

# Model
model = LinearRegression()
model.fit(X, y)

# Prediction
y_pred = model.predict(X)

# Coefficients
print("Intercept (B0):", model.intercept_)
print("Coefficients (B1, B2):", model.coef_)

# Evaluation
mse = mean_squared_error(y, y_pred)
rmse = np.sqrt(mse)
print("MSE:", mse)
print("RMSE:", rmse)

# Visualization
plt.scatter(y, y_pred)
plt.plot([y.min(), y.max()], [y.min(), y.max()], 'r--')
plt.xlabel("Actual Price")
plt.ylabel("Predicted Price")
plt.title("Actual vs Predicted (Multiple Linear Regression)")
plt.grid(True)
plt.show()
