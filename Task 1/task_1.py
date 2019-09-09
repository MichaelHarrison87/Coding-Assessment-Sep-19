import csv
from collections import OrderedDict
from datetime import datetime

import numpy as np


### Import Data

# Import data into a dict
with open('avocado.csv', mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)

    # Create dict template with first row - headers as keys, data items in a list as the dict's values
    row = next(csv_reader)
    data_dict = OrderedDict((key, [value]) for key, value in row.items())
    
    # Put the remaining rows into the dict:
    for row in csv_reader:
        for key, value in row.items():
            data_dict[key].append(value)

# So each column in the csv file corresponds to a key in data_dict, with the data values of each row stored 
# in associated lists.


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
'XLarge Bags'
]

for col in numeric_columns:
    data_dict[col] = [float(val) for val in data_dict[col]]

data_dict['year'] = [int(val) for val in data_dict['year']]


# Format the date:
data_dict['Date'] = [datetime.strptime(dt, '%Y-%m-%d').date() for dt in data_dict['Date']]

# Month might be a useful feature - e.g. to capture seasonality over the year
data_dict['Month'] = [dt.month for dt in data_dict['Date']]


# Now create dummy one-hot variables for categorical factors:
# Type
data_dict['type_dummy'] = [1 if avocado_type == 'organic' else 0 for avocado_type in data_dict['type']]

# Region
# First get a de-duplicated list of regions:
regions = set()
for region in data_dict['region']:
    regions.add(region)
regions = list(regions)

# Now using one region as a baseline, create the dummy variables (the baseline has all the dummy variables 0)
region_baseline = regions[0]
region_dummies = regions[1:]

for region in region_dummies:
    data_dict[region] = [1 if item == region else 0 for item in data_dict['region']]


### Set-up Model

# Put Data into NumPy Arrays
response = np.array(data_dict['AveragePrice'])

feature_columns = ['Month',
'year',
'Total Volume',
'type_dummy'                   
]
feature_columns.extend(region_dummies)

features = np.array([data_dict[feature] for feature in feature_columns])

# Transpose - so that each column of the matrix corresponds to a feature from the data (features are rows above)
features = features.T
