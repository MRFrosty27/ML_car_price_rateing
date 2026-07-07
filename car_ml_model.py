import matplotlib.pyplot as plt
import pandas as pd
import os, joblib, csv
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error,accuracy_score, precision_score, recall_score, f1_score
from car_web_scrape import Brand_names_autotrader as brand_names
from datetime import date
from re import sub

colors = ['#d62728', '#ff7f0e', '#ffdb58', '#2ca02c', '#1f77b4']  # red, orange, yellow, green, blue

user_input = int(input('press 1 to train model\npress 2 to use model\nenter: '))
if user_input == 1:
    script_path = os.path.dirname(os.path.abspath(__file__))
    new_folder_path = fr'{script_path}\{date.today()}'
    new_plot_folder_path = fr'{new_folder_path}\plot'
    with open(new_folder_path,'a',newline='',encoding='utf-8') as file:
        model_performance = csv.writer(file)
        model_performance.writerow(['Model_name','Accuracy_score','F1','Number_of_rows'])

    print('starting training')

    def plot_data(dataframe):
        plt.subplot(3,1)
        plt.figure(figsize=(16, 9))
        for rating in range(5):
            mask = dataframe['Price_rating_num'] == rating
            plt.scatter(dataframe.loc[mask, 'Price'], 
                        dataframe.loc[mask, 'Price_rating_num'],
                        c=colors[rating],
                        label=f'Rating {rating}')

        plt.xlabel('Price', fontsize=13)
        plt.ylabel('Price Rating (0-4)', fontsize=13)
        plt.title(f'Scatter Plot: Price vs Price Rating - {name} {model_name}', fontsize=15)
        plt.yticks([0, 1, 2, 3, 4])
        plt.grid(True, alpha=0.3, linestyle='-')
        plt.legend(title='Price Rating')

        plt.figure(figsize=(10, 6))
        plt.scatter(dataframe['Milage'], dataframe['Price'], alpha=0.7, c='steelblue', s=50)
        plt.xlabel('Mileage', fontsize=13)
        plt.ylabel('Price', fontsize=13)
        plt.title(f'Price vs Mileage - {name} {model_name}', fontsize=15)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

        plt.figure(figsize=(10, 6))
        plt.scatter(dataframe['Year'], dataframe['Price'], alpha=0.7, c='darkorange', s=50)
        plt.xlabel('Year', fontsize=13)
        plt.ylabel('Price', fontsize=13)
        plt.title(f'Price vs Year - {name} {model_name}', fontsize=15)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

        plt.show()
        plt.savefig(fr'{new_plot_folder_path}\{model_name}')

    def clean_model_name(model):
        global name
        words = str(model).split()
        words = [word.lower() for word in words]
        words = [sub(r'[^a-zA-Z0-9]', '', word) for word in words]
        words = [word.replace(' ','_') for word in words]
        return words

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
        filename = fr"{script_path}\autotrader_{name}_dataset.csv"
    
        if os.path.exists(filename):#check if they exist
            if os.path.getsize(filename) == 0: raise Warning(f'{filename} is empty')#raise error if empty

            temp_ds = pd.read_csv(filename,sep=',',dtype={"Brand": 'str', "Model": 'str',"Variant": 'str',"Year":'str',"Milage": 'str', "Manual_Automatic": 'category',"Price_rating": 'category', "Price": 'str'},header=0)
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
    
    for name, dataset in model_datasets.items():
        ds = dataset.copy()
        ds['Cleaned_Model'] = ds['Model'].apply(clean_model_name)
        for model_name in sorted(ds['Cleaned_Model'].unique()):#seperate all unique models into seperate datasets
            model_filename = f'{model_name}_ml_model.joblib'
            if os.path.exists(model_filename): 
                user_input = int(input('a model already exists\npress 1 to keep current model\npress 2 to retrain\nenter: '))
                if user_input == 1: continue
                elif user_input == 2: os.remove(model_filename)
                else:raise Warning('incorrect input')

            model_ds = ds[ds['Cleaned_Model'] == model_name].copy()
            model_ds['Price_rating_num'] = model_ds['Price_rating'].map(rating_map)#convert rating to int 
            plot_data(model_ds)
            #drop all rows with no rating
            train_ds = model_ds.dropna(subset=['Price_rating_num'])
            train_ds = train_ds[train_ds['Price_rating_num'] != 0]

            if len(train_ds) < 10: 
                print(f'was not enough data to create training dataset for {model_name}')
                continue

            x_train, x_test_accuracy, y_train, y_test_accuracy = train_test_split(train_ds[['Price', 'Year','Milage']],train_ds['Price_rating_num'],test_size=0.1)
            test_ds = train_ds[train_ds['Price_rating_num'] == 0]#use unrated rows for testing after accuracy test
            x_test = test_ds[['Price', 'Year','Milage']]
            y_test = test_ds['Price_rating_num']
            print(f"Training model for {name} - {model_name}...")
            model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
            model.fit(x_train, y_train)

            model_test_results = model.predict(x_test_accuracy)
            acc = accuracy_score(y_test_accuracy,model_test_results)
            f1 = f1_score(y_test_accuracy,model_test_results)
            #prec = precision_score(y_test_accuracy,model_accuracy_test_results)
            #rec = recall_score(y_test_accuracy,model_accuracy_test_results)
            #r2 = r2_score(y_test_accuracy,model_accuracy_test_results)
            #mae = mean_absolute_error(y_test_accuracy,model_accuracy_test_results)
            #mse = mean_squared_error(y_test_accuracy,model_accuracy_test_results)
            print(f'accuracy: {acc}\n f1: {f1}')
            model_performance.writerow([model_name,int(acc),int(f1),len(ds)])
            joblib.dump(model, model_filename)#store model

elif user_input == 2:
    script_path = os.path.dirname(os.path.abspath(__file__))
    available_brands = list(brand_names)
    while True:
        print("Available brands:")
        for i, brand in enumerate(available_brands, 1):
            print(f"{i}. {brand}")
        brand_idx = int(input("Select brand number: ")) - 1
        selected_brand = available_brands[brand_idx]
        filename = fr"{script_path}\autotrader_{selected_brand}_dataset.csv"
        if os.path.exists(filename):
            ds = pd.read_csv(filename)
            print(f"Loaded: {filename}")
        else:
            print(f"Warning: {filename} not found. Skipping {selected_brand}.")
            continue
    
        available_models = sorted(ds['Cleaned_Model'].unique(),key=str)
        print(fr"Available models for {selected_brand}:")
        for i, model in enumerate(available_models, 1):
            print(f"{i}. {model}")
        model_idx = int(input("Select model number: ")) - 1
        selected_model = available_models[model_idx]
        selected_model = selected_model.replace(selected_brand,'')
        selected_model = selected_model[1:]
        model_filename = f'{script_path}\{selected_model}_ml_model.joblib'
        if not os.path.exists(model_filename):
            print(f"Model file {model_filename} not found.") 
        else:
            model = joblib.load(model_filename)
            price = int(input("Enter car price: Rand "))
            year = int(input("Enter car year: "))
            milage = int(input('Enter car milage: '))
            user_data = pd.DataFrame([[price, year,milage]],columns=model.feature_names_in_)
            prediction = model.predict(user_data)[0]
            rating_map = ['No Rating','High Price','Low Price','Fair Price','Great Price']
            print(fr"The car's price rating is: {rating_map[prediction]}")