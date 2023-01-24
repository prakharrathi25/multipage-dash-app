import pandas as pd
import numpy as np


## reading the dataset
# pd_2 = pd.read_csv('https://raw.githubusercontent.com/Anmol3015/Plotly_Dash_examples/main/retail_sales.csv', sep=',')

pd_2['Date'] = pd.to_datetime(pd_2['Date'], format='%Y-%m-%d')


################################ total sales Month level  ###################################
monthly_sales_df = pd_2.groupby(['month','Month']).agg({'Weekly_Sales':'sum'}).reset_index()


################################ holiday sales month lvl #####################################
holiday_sales = pd_2[pd_2['IsHoliday'] == 1].groupby(['month'])['Weekly_Sales'].sum().reset_index().rename(columns={'Weekly_Sales':'Holiday_Sales'})

############################# combined #########################
monthly_sales_df  = pd.merge(holiday_sales,monthly_sales_df,on = 'month', how = 'right').fillna(0)

############################## rounding sales to 1 decimal #############################
monthly_sales_df['Weekly_Sales'] = monthly_sales_df['Weekly_Sales'].round(1)
monthly_sales_df['Holiday_Sales'] = monthly_sales_df['Holiday_Sales'].round(1)


###################### weekly sales #########################
weekly_sale = pd_2.groupby(['month','Month','Date']).agg({'Weekly_Sales':'sum'}).reset_index()
weekly_sale['week_no'] = weekly_sale.groupby(['Month'])['Date'].rank(method='min')


########################### store level sales #######################
store_df=pd_2.groupby(['month','Month','Store']).agg({'Weekly_Sales':'sum'}).reset_index()
store_df['Store'] = store_df['Store'].apply(lambda x: 'Store'+" "+str(x))
store_df['Weekly_Sales'] = store_df['Weekly_Sales'].round(1)


######################## dept level sales #########################
dept_df=pd_2.groupby(['month','Month','Dept']).agg({'Weekly_Sales':'sum'}).reset_index()
dept_df['Dept'] = dept_df['Dept'].apply(lambda x: 'Dept'+" "+str(x))
dept_df['Weekly_Sales'] = dept_df['Weekly_Sales'].round(1)
