import time
from typing import List, Dict, Any
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import numpy as np

class Swirl:
    def __init__(self, user_preferences: Dict[str, Any]):
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 10)
        self.user_preferences = user_preferences
        self.task_goal = None

    def set_task_goal(self, goal: Dict[str, Any]):
        """
        Set the current task goal.
        """
        self.task_goal = goal

    def evaluate_flight_options(self, flights: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evaluate flight options based on user preferences and task goal.
        """
        if not self.task_goal or 'destination' not in self.task_goal or 'date' not in self.task_goal:
            raise ValueError("Task goal must include destination and date.")

        def score_flight(flight):
            score = 0
            # Price
            if self.user_preferences.get('max_price', float('inf')) > flight['price']:
                score += 1
            else:
                score -= 1  
            
            if self.user_preferences.get('max_duration', float('inf')) > flight['duration']:
                score += 1
            else:
                score -= 1 
            
            preferred_time = self.user_preferences.get('preferred_time', None)
            if preferred_time:
                time_diff = abs(flight['departure_time'] - preferred_time)
                score -= time_diff / 3600  

            if self.user_preferences.get('preferred_airline') == flight['airline']:
                score += 1

            if flight['airline'] in self.user_preferences.get('frequent_airlines', []):
                score += 0.5

            return score

        scored_flights = sorted(flights, key=score_flight, reverse=True)
        return scored_flights[0] if scored_flights else None

    def parse_flight_options(self) -> List[Dict[str, Any]]:
        """
        Parse flight options from the current web page.
        """

        flights = []
        flight_elements = self.driver.find_elements(By.CLASS_NAME, "flight-item")
        for element in flight_elements:
            price = float(element.find_element(By.CLASS_NAME, "price").text.replace('$', ''))
            duration = int(element.find_element(By.CLASS_NAME, "duration").text.split(' ')[0]) 
            departure_time = int(element.find_element(By.CLASS_NAME, "departure-time").text.replace(':', ''))
            airline = element.find_element(By.CLASS_NAME, "airline").text
            
            flights.append({
                'price': price,
                'duration': duration,
                'departure_time': departure_time,
                'airline': airline
            })
        return flights

    def select_flight(self, flight: Dict[str, Any]):
        """
        Select the flight from the web page.
        """
        flight_index = next((index for index, f in enumerate(self.parse_flight_options()) if f['price'] == flight['price']), None)
        if flight_index is not None:
            flight_elements = self.driver.find_elements(By.CLASS_NAME, "flight-item")
            flight_elements[flight_index].find_element(By.CLASS_NAME, "select-flight").click()

    def execute_task(self, task_description: str):
        """
        Execute the task of booking a flight based on user preferences and task goal.
        """
        self.set_task_goal({'destination': 'Tokyo', 'date': '2025-01-01'}) 
        
        self.driver.get("example-flight-booking-site.com")
        
        self.wait.until(EC.element_to_be_clickable((By.ID, "destination"))).send_keys(self.task_goal['destination'])
        self.wait.until(EC.element_to_be_clickable((By.ID, "departure_date"))).send_keys(self.task_goal['date'])
        self.wait.until(EC.element_to_be_clickable((By.ID, "search_flights"))).click()
        
        time.sleep(5) 
        
        flights = self.parse_flight_options()
        best_flight = self.evaluate_flight_options(flights)
        
        if best_flight:
            print(f"Best flight selected: {best_flight}")
            self.select_flight(best_flight)

        else:
            print("No suitable flights found.")

        print("Task execution completed.")
        self.driver.quit()

user_preferences = {
    'max_price': 500,
    'max_duration': 12,
    'preferred_time': 1000, 
    'preferred_airline': 'AirJapan',
    'frequent_airlines': ['AirJapan', 'ANA']
}

voyant = Voyant(user_preferences)
voyant.execute_task("Book a flight to Tokyo on January 1st, 2025")
