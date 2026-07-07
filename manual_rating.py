import os
import pandas as pd
from car_web_scrape import Brand_names_autotrader as brand_names
from car_ml_model import clean_model_name, plot_data
import matplotlib.pyplot

model_datasets = {}
for name in brand_names:
    script_path = os.path.dirname(os.path.abspath(__file__))
    filename = fr"{script_path}\autotrader_{name}_dataset.csv"
    if os.path.exists(filename):
        ds = pd.read_csv(filename,sep=',',dtype={"Brand": 'str', "Model": 'str',"Variant": 'str',"Year":'str',"Milage": 'str', "Manual_Automatic": 'category',"Price_rating": 'category', "Price": 'str'},header=0)
        print(f"Loaded: {filename}")
        ds['Cleaned_Model'] = ds['Model'].apply(clean_model_name)
        for model_name in sorted(ds['Cleaned_Model'].unique()):
            ds['Cleaned_Model' == model_name]
    else:
            print(f"Warning: {filename} not found. Skipping {name}.")