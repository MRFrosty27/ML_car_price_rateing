from xmlrpc.client import DateTime
import matplotlib.pyplot as plt
import pandas as pd
import os, joblib, csv
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error,accuracy_score, precision_score, recall_score, f1_score
from car_web_scrape import Brand_names_autotrader as brand_names
from datetime import date,datetime
from re import sub,compile

colors = ['#d62728', '#ff7f0e', '#ffdb58', '#2ca02c', '#1f77b4']  # red, orange, yellow, green, blue
# Mapping from string rating to numeric value
rating_map = {
'No Rating': 0,
'High Price': 1,
'Low Price': 2,
'Fair Price': 3,
'Great Price': 4
}

def clean_model_name(model):
    words = str(model).split()
    words = [word.lower() for word in words]
    words = [sub(r'[^a-zA-Z0-9]', '', word) for word in words]
    words = [word.replace(' ','_') for word in words]
    words = '_'.join(words)
    return words

if __name__ == '__main__':
    user_input = int(input('press 1 to train model\npress 2 to use model\nenter: '))
    if user_input == 1:
        script_path = os.path.dirname(os.path.abspath(__file__))
        new_folder_path = fr'{script_path}\{date.today()}'
        new_plot_folder_path = fr'{new_folder_path}\plot'
        if not os.path.exists(new_folder_path):
            os.mkdir(fr'{new_folder_path}',mode=0o777)

        with open(fr'{new_folder_path}\model_training_results.csv','a',newline='',encoding='utf-8') as file:
            model_performance = csv.writer(file)
            model_performance.writerow(['Model_name','Accuracy_score(%)','F1(%)','Number_of_rows'])

        print('starting training')

        def plot_data(dataframe):
            fig, (subp1,subp2,subp3) = plt.subplots(1, 3, figsize=(15, 5))
            for rating in range(5):
                mask = dataframe['Price_rating_num'] == rating
                subp1.scatter(dataframe.loc[mask, 'Price'], 
                            dataframe.loc[mask, 'Price_rating_num'],
                            c=colors[rating],
                            label=f'Rating {rating}')

            subp1.set_title(f'Scatter Plot: Price vs Price Rating - {name} {model_name}', fontsize=15)
            subp1.grid(True, alpha=0.3, linestyle='-')
            subp1.legend(title='Price Rating')

            subp2.scatter(dataframe['Milage'], dataframe['Price'], alpha=0.7, c='steelblue')
            subp2.set_title(f'Price vs Mileage - {name} {model_name}', fontsize=15)
            subp2.grid(True, alpha=0.3)

            subp3.scatter(dataframe['Year'], dataframe['Price'], alpha=0.7, c='darkorange')
            subp3.set_title(f'Price vs Year - {name} {model_name}', fontsize=15)
            subp3.grid(True, alpha=0.3)

            plt.show()
            #plt.savefig(fr'{new_plot_folder_path}\{model_name}')

        model_datasets = {}

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
                temp_ds['Year'] = pd.to_numeric(temp_ds['Year'])
                temp_ds.dropna(subset=['Model'],inplace=True)
                model_datasets[name] = temp_ds
                print(f"Loaded: {filename}")
            else:
                print(f"Warning: {filename} not found. Skipping {name}.")
        print('Loading data completed')
    
        for name, dataset in model_datasets.items():
            ds = dataset.copy()
            ds['Cleaned_Model'] = ds['Model'].apply(clean_model_name)
            for model_name in sorted(ds['Cleaned_Model'].unique()):#seperate all unique models into seperate datasets
                model_filename = fr'{new_folder_path}\{model_name}_ml_model.joblib'
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
                f1 = f1_score(y_test_accuracy,model_test_results,average='weighted')
                #prec = precision_score(y_test_accuracy,model_accuracy_test_results)
                #rec = recall_score(y_test_accuracy,model_accuracy_test_results)
                #r2 = r2_score(y_test_accuracy,model_accuracy_test_results)
                #mae = mean_absolute_error(y_test_accuracy,model_accuracy_test_results)
                #mse = mean_squared_error(y_test_accuracy,model_accuracy_test_results)
                print(f'accuracy: {acc}\n f1: {f1}')
                with open(fr'{new_folder_path}\model_training_results.csv','a',newline='',encoding='utf-8') as file:
                    model_performance = csv.writer(file)
                    model_performance.writerow([model_name,int(acc*100),int(f1*100),len(ds)])
                joblib.dump(model, model_filename)#store model

    elif user_input == 2:
        script_path = os.path.dirname(os.path.abspath(__file__))
        pattern = compile(r'^\d{4}-\d{2}-\d{2}')
        date_files = []
        for f in os.listdir(script_path):
            if os.path.isdir(os.path.join(script_path, f)):
                match = pattern.match(f)
                if match:
                    try:
                        datetime.strptime(match.group(0), '%Y-%m-%d')
                        date_files.append(f)
                    except ValueError:
                        continue 

        date_files.sort()
        
        while True:
            #select a folder that contains the a model with the naming convention of the date of training(yyyy-mm-dd)
            print('Model training date:')
            for i, folder in enumerate(date_files, 1):
                print(f"{i}. {folder}")
            selected_folder = date_files[int(input("Select folder: ")) - 1]

            #select the model for a specific brand
            model_details = pd.read_csv(fr'{script_path}\{selected_folder}\model_training_results.csv',)
            model_name_list = model_details['Model_name'].to_list()
            for i, model_name in enumerate(model_name_list, 1):
                print(f"{i}. {model_name}")
            selected_model = model_name_list[int(input("Select car model: ")) - 1]

            #find the model
            model_path = os.path.join(script_path, selected_folder, fr'{selected_model}_ml_model.joblib')
            if os.path.isfile(model_path):
    
                model = joblib.load(model_path)
                price = int(input("Enter car price: Rand "))
                year = int(input("Enter car year: "))
                milage = int(input('Enter car milage: '))
                user_data = pd.DataFrame([[price, year,milage]],columns=model.feature_names_in_)
                prediction = model.predict(user_data)[0]
                rating_map = ['No Rating','High Price','Low Price','Fair Price','Great Price']
                print(fr"The car's price rating is: {rating_map[prediction]}")
            else: print(f'Model was not found\npath: {model_path}')#D:\Python code\cloned repo\text__to_code_model\2026-07-09\toyota_hilux_ml_model.joblib