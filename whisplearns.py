import time
from typing import List, Dict, Any
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import joblib

class Swirl:
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 10)
        self.interaction_log = []
        self.model = None
        self.load_model()

    def load_model(self):
        """
        Load or initialize the machine learning model for decision making.
        """
        try:
            self.model = joblib.load('voyant_model.joblib')
        except FileNotFoundError:
            self.model = RandomForestRegressor()
            print("No model found. Initialized a new model.")

    def save_model(self):
        """
        Save the current machine learning model to disk.
        """
        joblib.dump(self.model, 'voyant_model.joblib')

    def log_interaction(self, interaction: Dict[str, Any]):
        """
        Log interaction details for learning purposes.
        """
        self.interaction_log.append(interaction)

    def prepare_data(self) -> pd.DataFrame:
        """
        Prepare interaction data for machine learning.
        """
        df = pd.DataFrame(self.interaction_log)
        return df

    def train_model(self):
        """
        Train the machine learning model on past interactions.
        """
        if not self.interaction_log:
            print("No interaction data to train on.")
            return

        df = self.prepare_data()
        if 'outcome' not in df.columns or df['outcome'].isnull().all():
            print("No outcome data to train on.")
            return

        features = df.drop(columns=['outcome'])
        X = features.select_dtypes(include=[np.number]).values 
        y = df['outcome'].values

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        self.model.fit(X_train, y_train)
        
        self.save_model()

    def predict_action(self, current_state: Dict[str, Any]) -> str:
        """
        Predict the best action based on current state using the trained model.
        """
        if self.model is None:
            print("Model not trained or loaded. Using default action.")
            return "Default Action"  

        features = pd.DataFrame([current_state]).select_dtypes(include=[np.number]).values
        prediction = self.model.predict(features)
        
        action_map = {0: "Click Button", 1: "Fill Form", 2: "Navigate"}
        return action_map.get(int(prediction[0]), "Unknown Action")

    def perform_action(self, action: str):
        """
        Perform the predicted action on the website.
        """
        if action == "Click Button":
            self.driver.find_element(By.ID, "submit").click()
        elif action == "Fill Form":
            self.driver.find_element(By.ID, "name").send_keys("John Doe")
        elif action == "Navigate":
            self.driver.get("example.com/new_page")
        else:
            print(f"Unhandled action: {action}")

    def execute_task(self, task_description: str):
        """
        Execute a task by learning from past interactions and making decisions.
        """
        self.driver.get("example.com")
        
        for _ in range(5): 
            current_state = {
                'page_load_time': np.random.uniform(1, 5),
                'button_clicks': np.random.randint(0, 3),
                'form_fields_filled': np.random.randint(0, 5),
                'outcome': np.random.uniform(0, 1) 
            }
            self.log_interaction(current_state)
            
            action = self.predict_action(current_state)
            self.perform_action(action)
            time.sleep(2) 

        self.train_model()
        
        final_state = {
            'page_load_time': 3,
            'button_clicks': 1,
            'form_fields_filled': 2
        }
        final_action = self.predict_action(final_state)
        self.perform_action(final_action)

        print("Task execution completed with learning from past interactions.")
        self.driver.quit()

swirl = Swirl()
swirl.execute_task("Complete a form on the website")
