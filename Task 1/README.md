# Task 1 - Linear Regression Model

## Data Observations
* Data is made up of weekly observations over the period Jan-2015 to Mar-2018 (inclusive), collected on Sundays each week.

* For each weekly observation, we have the average price of both conventional and organic avocados, across 54 US regions.

* This data is complete except for 3 observations - organic in the region WestTexNewMexico is missing for 3 weeks: 06-Dec-2015, 18-Jun-2017, 25-Jun-2017. However this shouldn't affect the analysis.

* So in total we have 18,249 observations. The average price varies between 0.44 and 3.25 over the entire set of data.

* The other features in the data seem to be volume measures - Total Volume presumably being total numbers of avocados sold, while Total Bags being number of "bags" (packages?). Total Bags is broken down by size in the data - small, large, XL. 

* There are also 3 numerical field names (4046, 4225, 4770), but it's not clear what these are. However, adding them to Total Bags matches Total Volume - so these also seem to be volume measures.

* These volume measures are all very highly correlated with one another - e.g. 4046 has a correlation coefficient of 0.98 with Total Volume - which makes sense, as they all measure (different aspects of) the same thing. However this means they're highly colinear, and so shouldn't all be included in a linear regression.

* So of these fields, we'll include only Total Volume in the regression model. Albeit, the causation is the wrong way round - as volume will be more driven by the price, rather than vice versa. However we'll ignore this for the sake of this exercise.

* The region column is made up of non-mutually-exclusive regions at different geographical levels - for instance, it contains both Los Angeles and California, despite LA being _in_ California. There is also "TotalUS" category, covering the entire country.

* In the model, we need to remove this overlap across observations - as linear regression assumes all observations are independant (where, clearly, LA and California won't be). We'll restrict ourselves to the broad regions - North East, South East, Great Lakes etc - rather than the more granular city-level data. As this gives fewer model parameters to interpret, and should be less noisy. 

* Note: adding up the Total Volume for the regions we chose matches the Total Volume for the "TotalUS" category, so this implies our choice of regions are mutually exclusive and cover the whole country. (The set includes both California and "West", but these seem to be distinct).

## Model Results
The model coefficients are below - note the baseline type is "conventional" and the baseline region is "West":

    intercept: -108.23
    year: 0.05
    Month: 0.02
    Total Volume: -5.08e-09
    type_dummy: 0.49
    California: -0.00
    SouthCentral: -0.30
    Northeast: 0.20
    Southeast: -0.01
    GreatLakes: -0.07
    Midsouth: -0.00
    Plains: 0.03

So these imply the average price of avocados increased by about 5.5 cents per year. While, within a year, the price increases around 2.2 cents per month -  

The coefficient for Total Volume is extremely small - due to the magnitude of the Total Volume values. Further analysis could take log(Total Volume) to help account for this. Nevertheless, the coefficient is negative - suggesting price is negatively correlated with volume, which is intuitive (higher prices, lower volumes).

"type_dummy" suggests that organic avocados are on average around 50 cents more expensive than conventional ones.

Most of the regions are broadly comparable in price to the baseline West (California especially so - which stands to reason). Except North East and South Central stand out as notably more and less expensive respectively (the former by 20 cents, the latter by 30 cents). 

South Central may be cheaper as this might be the main region where avocados are grown - hence will have a higher supply (and probably demand, at least per person), and so lower prices. Although a general lower cost of living in the region is likely also part of the explanation.

North East perhaps face difficulties of supply in winter - explaining why it is notably more expensive. Further analysis could put a region:month interaction term in the model to explore how regional pricing varies over a year.

Albeit this model has a R^2 of only 0.44 - so it only explains 44% of the variation in the data.