import csv
from collections import OrderedDict
from datetime import datetime

import numpy as np


### Import Data

# Read the data into a dict
with open('avocado.csv', mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)

    # Create dict template with first row - headers as keys, data items in a list as the dict's values
    row = next(csv_reader)
    data_dict = OrderedDict((key, [value]) for key, value in row.items())
    
    # Put the remaining rows into the dict:
    for row in csv_reader:
        for key, value in row.items():
            data_dict[key].append(value)

# So each column in the csv file corresponds to a key in data_dict, with each row's data items stored 
# in associated lists (i.e. data_dict's values).


### Preprocess Data

# Format numeric columns to floats (currently they're strings):
numeric_columns = ['AveragePrice',
'Total Volume',
'4046',
'4225',
'4770',
'Total Bags',
'Small Bags',
'Large Bags',
'XLarge Bags',
'year'
]

for col in numeric_columns:
    data_dict[col] = [float(val) for val in data_dict[col]]

# Format the date:
data_dict['Date'] = [datetime.strptime(dt, '%Y-%m-%d').date() for dt in data_dict['Date']]

# Month might be a useful feature - e.g. to capture seasonality over the year
data_dict['Month'] = [dt.month for dt in data_dict['Date']]


# Now create dummy one-hot variables for the categorical factors:
# Type
data_dict['type_dummy'] = [1 if avocado_type == 'organic' else 0 for avocado_type in data_dict['type']]

# Region
# As mentioned in the README, we look only at the broad regions encompassing the whole country, rather 
# than city-level data:
regions = ['West',
'California',
'SouthCentral',
'Northeast',
'Southeast',
'GreatLakes',
'Midsouth',
'Plains'
]

# Now using one region as a baseline, create the dummy variables (the baseline has all the dummy variables 0)
region_baseline = regions[0]
region_dummies = regions[1:]

for region in region_dummies:
    data_dict[region] = [1 if item == region else 0 for item in data_dict['region']]


### Set-up Model

# Add intercept column - columns of 1's representing linear model's intercept term
data_dict["intercept"] = np.ones(len(data_dict['AveragePrice']))

# Put Data into NumPy Arrays
response = np.array(data_dict['AveragePrice'])

# Create feature matrix - each feature as a column (and each row as an observation)
feature_columns = ['intercept',
'year',
'Month',
'Total Volume',
'type_dummy'                   
]
feature_columns.extend(region_dummies)

feature_matrix = np.column_stack([data_dict[feature] for feature in feature_columns])


### Fit Model

# np.linalg.lstsq(A, b) below calculates the least-squares solution x to the (matrix) equation:  Ax = b
# i.e. the linear regression coefficients. The function returns a tuple with values: 
# (x, sum of squares of residuals (i.e. Euclidean norm ||Ax-b||), rank of A, singular values of A)
model_coeffs, sumsq_resids, rank_fm, singular_values_fm  = np.linalg.lstsq(feature_matrix, response, rcond=None)

# Alternatively, we could have found the coefficients using the Normal Equations:
model_coeffs_alt = np.linalg.inv(feature_matrix.T @ feature_matrix) @ feature_matrix.T @ response

# Below we calculate R^2, the coefficient of determination:
sumsq_total = np.sum((response - np.mean(response))**2)
r_squared = 1 - sumsq_resids/sumsq_total


### Results

results = {feature: coeff for feature, coeff in zip(feature_columns, model_coeffs)}

for feature, coeff in results.items():
    print(f'{feature}: {coeff:.2f}')
print(r_squared)