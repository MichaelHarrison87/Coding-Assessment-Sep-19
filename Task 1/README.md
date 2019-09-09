# Task 1 - Linear Regression Model

## Data Observations
* Data is made up of weekly observations over the period Jan-2015 to Mar-2018 (inclusive), collected on Sundays each week.

* For each weekly observation, we have the average price of both conventional and organic avocados, across 54 US regions.

* This data is complete except for 3 observations - organic in the region WestTexNewMexico is missing for 3 weeks: 06-Dec-2015, 18-Jun-2017, 25-Jun-2017. However this shouldn't affect the analysis.

* So in total we have 18,249 observations. The average price varies between 0.44 and 3.25 over the entire set of data.

* The other features in the data seem to be volume measures - Total Volume presumably being total numbers of avocados sold, while Total Bags being number of "bags" (packages?). Total Bags is broken down by size in the data - small, large, XL. 

* There are also 3 numerical field names (4046, 4225, 4770), but it's not clear what these are. However, adding them to Total Bags matches Total Volume - so these also seem to be volume measures.

* These volume measures are all very highly correlated with one another - e.g. 4046 has a correlation coefficient of 98% with Total Volume - which makes sense, as they all measure (different aspects of) the same thing. However this means they're highly colinear, and so shouldn't all be included in a linear regression.

* So of these fields, we'll include only Total Volume in the regression model. Albeit, the causation is the wrong way round - as volume will be more driven by the price, rather than vice versa. However we'll ignore this for the sake of this exercise.