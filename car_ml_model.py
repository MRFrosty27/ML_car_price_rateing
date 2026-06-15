import matplotlib.pyplot as plt
import pandas as pd
import os, joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error,accuracy_score, precision_score, recall_score, f1_score
from car_web_scrape import Brand_names_autotrader as brand_names

colors = ['#d62728', '#ff7f0e', '#ffdb58', '#2ca02c', '#1f77b4']  # red, orange, yellow, green, blue

user_input = int(input('press 1 to train model\npress 2 to use model\nenter: '))
if user_input == 1:
    print('starting training')
    def plot_data(dataframe):
        plt.figure(figsize=(10, 6))
        for rating in range(5):
            mask = dataframe['Price_rating_num'] == rating
            plt.scatter(dataframe.loc[mask, 'Price'], 
                        dataframe.loc[mask, 'Price_rating_num'],
                        c=colors[rating],
                        label=f'Rating {rating}',
                        s=70, alpha=0.85, edgecolors='black', linewidth=0.6)

        plt.xlabel('Price', fontsize=13)
        plt.ylabel('Price Rating (0-4)', fontsize=13)
        plt.title(f'Scatter Plot: Price vs Price Rating - {name}', fontsize=15)
        plt.yticks([0, 1, 2, 3, 4])
        plt.grid(True, alpha=0.3, linestyle='--')
        plt.legend(title='Price Rating')
        plt.show()

    def clean_model_name(model):
        global name
        words = str(model).split()
        cleaned_words = [w for w in words if w.lower() != name.lower()]
        cleaned = ' '.join(cleaned_words).strip()
        return cleaned if cleaned else model

    model_datasets = {}
    # Mapping from string rating to numeric value
    rating_map = {
        'No Rating': 0,
        'High Price': 1,
        'Low Price': 2,
        'Fair Price': 3,
        'Great Price': 4
    }

    for name in brand_names:
        #find all csv files
        script_path = os.path.dirname(os.path.abspath(__file__))
        filename = fr"{script_path}\autotrader_{name}_dataset.csv"
    
        if os.path.exists(filename):#check if they exist
            if os.path.getsize(filename) == 0: raise Warning(f'{filename} is empty')#raise error if empty

            temp_ds = pd.read_csv(filename,sep=',',dtype={"Brand": 'str', "Model": 'str',"Variant": 'str',"Year":'str',"Milage": 'str', "Manual_Automatic": 'category',"Price_rating": 'category', "Price": 'str'},header=0)
            print(temp_ds[['Model','Milage', 'Year','Price']].head(5))
            #ensure that columns Milage, Year and Price only contain numbers
            temp_ds['Milage'] = temp_ds['Milage'].str.replace(r'[^0-9]', '', regex=True)
            temp_ds['Price'] = temp_ds['Price'].str.replace(r'[^0-9]', '', regex=True)
            temp_ds['Year'] = temp_ds['Year'].str.replace(r'[^0-9]', '', regex=True)
            #convert to numeric
            temp_ds['Milage'] = pd.to_numeric(temp_ds['Milage'])
            temp_ds['Price'] = pd.to_numeric(temp_ds['Price'])
            temp_ds['Year'] = pd.to_numeric(temp_ds['Price'])
            print(temp_ds[['Model','Milage', 'Year','Price']].head(5))
            model_datasets[name] = temp_ds
            print(f"Loaded: {filename}")
        else:
            print(f"Warning: {filename} not found. Skipping {name}.")
    print('completed training')
    
    for name, ds in model_datasets.items():
        ds = ds.copy()
        print(ds.head(5))
        ds['Cleaned_Model'] = ds['Model'].apply(clean_model_name)
        print(ds['Cleaned_Model'].head(10))
        for model_name in sorted(ds['Cleaned_Model'].unique()):#seperate all unique models into seperate datasets
            model_ds = ds[ds['Cleaned_Model'] == model_name].copy()
            model_ds['Price_rating_num'] = model_ds['Price_rating'].map(rating_map)#convert rating to int 
            plot_data(model_ds)
            #drop all rows with no rating
            train_ds = model_ds.dropna(subset=['Price_rating_num'])
            train_ds = train_ds[train_ds['Price_rating_num'] != 0]
            if len(train_ds) == 0: raise Warning(f'could not create training data for {model_name}')
            x_train, x_test_accuracy, y_train, y_test_accuracy = train_test_split(train_ds[['Price', 'Year','Milage']],train_ds['Price_rating_num'],test_size=0.1)
            test_ds = train_ds[train_ds['Price_rating_num'] == 0]#use unrated rows for testing after accuracy test
            x_test = test_ds[['Price', 'Year','Milage']]
            y_test = test_ds['Price_rating_num']
            print(f"Training model for {name} - {model_name}...")
            model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
            print(x_train.head(10))
            print(y_train.head(10))
            model.fit(x_train, y_train)
            model_accuracy_test_results = model.predict(x_test_accuracy,y_test_accuracy)
            acc = accuracy_score(
            prec = precision_score(
            rec = recall_score(
            f1 = f1_score(
            r2 = r2_score(
            mae = mean_absolute_error(
            mse = mean_squared_error(
            model_filename = f'{model_name}_ml_model.joblib'#store model
            joblib.dump(model, model_filename)

elif user_input == 2:
    script_path = os.path.dirname(os.path.abspath(__file__))
    available_brands = list(brand_names)
    print("Available brands:")
    for i, brand in enumerate(available_brands, 1):
        print(f"{i}. {brand}")
    brand_idx = int(input("Select brand number: ")) - 1
    selected_brand = available_brands[brand_idx]
    filename = fr"{script_path}\autotrader_{selected_brand}_dataset.csv"
    if os.path.exists(filename):
        dataset = pd.read_csv(filename)
        print(f"Loaded: {filename}")
    else:
        print(f"Warning: {filename} not found. Skipping {selected_brand}.")
    
    available_models = sorted(dataset['Model'].unique())
    print(fr"\nAvailable models for {selected_brand}:")
    for i, model in enumerate(available_models, 1):
        print(f"{i}. {model}")
    model_idx = int(input("Select model number: ")) - 1
    selected_model = available_models[model_idx]
    model_filename = f'{selected_model}_ml_model.joblib'
    if not os.path.exists(model_filename):
        print(f"Model file {model_filename} not found.")
    else:
        model = joblib.load(model_filename)
        price = float(input("\nEnter car price: "))
        year = int(input("Enter car year: "))
        prediction = model.predict([[price, year]])[0]
        rating_map = {0:'No Rating',1:'High Price',2:'Low Price',3:'Fair Price',4:'Great Price'}
        print(fr"\nThe car's price rating is: {rating_map[prediction]}")