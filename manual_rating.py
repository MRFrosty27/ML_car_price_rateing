from cProfile import label
import os
from turtle import title
from numpy import spacing
import pandas as pd
from car_web_scrape import Brand_names_autotrader as brand_names
from car_ml_model import clean_model_name, colors, rating_map
import matplotlib.pyplot as plt

model_datasets = {}
for name in brand_names:
    script_path = os.path.dirname(os.path.abspath(__file__))
    filename = fr"{script_path}\autotrader_{name}_dataset.csv"
    if os.path.exists(filename):
        ds = pd.read_csv(filename,sep=',',dtype={"Brand": 'str', "Model": 'str',"Variant": 'str',"Year":'str',"Milage": 'str', "Manual_Automatic": 'category',"Price_rating": 'category', "Price": 'str'},header=0)
        print(f"Loaded: {filename}")
        #ensure that columns Milage, Year and Price only contain numbers
        ds['Milage'] = ds['Milage'].str.replace(r'[^0-9]', '', regex=True)
        ds['Price'] = ds['Price'].str.replace(r'[^0-9]', '', regex=True)
        ds['Year'] = ds['Year'].str.replace(r'[^0-9]', '', regex=True)
        #convert to numeric
        ds['Milage'] = pd.to_numeric(ds['Milage'])
        ds['Price'] = pd.to_numeric(ds['Price'])
        ds['Year'] = pd.to_numeric(ds['Year'])
        ds.dropna(inplace=True)
        ds['Model'] = ds['Model'].apply(clean_model_name)
        ds['Price_rating_num'] = ds['Price_rating'].map(rating_map)
        
        print(ds.head(10))
        #access models within brands
        for model_name in sorted(ds['Model'].unique()):
            ds_temp = ds[(ds['Model'] == model_name) & (ds['Price_rating'] == 'No Rating')]
            for row in ds_temp.itertuples():#plot all labeled data, then plot a single unlabeled data point for manual rating
                fig, (subp1,subp2,subp3) = plt.subplots(1, 3, figsize=(15, 5))
                for ax in (subp1, subp2, subp3):
                    ax.ticklabel_format(style='plain', axis='both')
                subp1.get_xaxis().set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))
                subp2.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))
                subp3.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))
                for rating in range(1,5):
                    mask = ds['Price_rating_num'] == rating
                    subp1.scatter(ds.loc[mask, 'Price'], 
                                ds.loc[mask, 'Price_rating_num'],
                                c=colors[rating],
                                label=f'Rating {rating}')

                subp1.scatter(row.Price,0,
                            c=colors[0],
                            label=f'Rating {0}')
                subp1.set_title(f'Scatter Plot: Price vs Price Rating - {name} {model_name}', fontsize=15)
                subp1.grid(True, alpha=0.3, linestyle='-')
                subp1.legend(title='Price Rating')

                subp2.scatter(ds['Milage'],ds['Price'],c=colors[1],label='milage')
                subp2.scatter(row.Milage,row.Price,c=colors[2],label='eval')
                subp2.set_title(f'Scatter Plot: Milage vs Price - {name} {model_name}', fontsize=15)
                subp2.grid(True, alpha=0.3, linestyle='-')
                subp2.legend()

                subp3.scatter(ds['Year'],ds['Price'],c=colors[1],label='year')
                subp3.scatter(row.Year,row.Price,c=colors[2],label='eval')
                subp3.set_title(f'Scatter Plot: Year vs Price - {name} {model_name}', fontsize=15)
                subp3.grid(True, alpha=0.3, linestyle='-')
                subp3.legend()

                plt.show()

    else:
            print(f"Warning: {filename} not found. Skipping {name}.")