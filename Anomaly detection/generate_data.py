import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os
import shutil

# Configuration
NUM_EVENTS = 100000
ANOMALY_RATE = 0.05
OUTPUT_FILE = 'auth_logs.csv'
BACKUP_FILE = 'auth_logs_backup.csv'

# Constants
DEPARTMENTS = ['Sales', 'Engineering', 'Finance', 'HR', 'Marketing', 'IT', 'Operations']
ROLES = ['Employee', 'Manager', 'Director', 'VP', 'Intern']
LOCATIONS = ['Mumbai', 'Bangalore', 'Delhi', 'Hyderabad', 'Chennai', 'Pune', 'Kolkata']
FOREIGN_LOCATIONS = ['New York', 'London', 'Moscow', 'Beijing', 'Tokyo', 'Dubai', 'Sydney', 'Nigeria', 'Russia', 'China']

USERS = [f'user_{i:03d}' for i in range(1, 201)] # 200 Unique users
USER_DETAILS = {
    u: {
        'name': f'User {u}',
        'dept': random.choice(DEPARTMENTS),
        'role': random.choice(ROLES),
        'home_loc': random.choice(LOCATIONS)
    } for u in USERS
}

def generate_ip(is_internal=True):
    if is_internal:
        return f"192.168.{random.randint(1, 20)}.{random.randint(1, 254)}"
    else:
        # Generate random public IP
        return f"{random.randint(1, 220)}.{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}"

def generate_timestamp():
    # Generate timestamp within last 30 days
    end_time = datetime.now()
    start_time = end_time - timedelta(days=30)
    random_seconds = random.randint(0, int((end_time - start_time).total_seconds()))
    return start_time + timedelta(seconds=random_seconds)

def generate_normal_event(event_id):
    user_id = random.choice(USERS)
    user = USER_DETAILS[user_id]
    
    # 95% chance of working hours (9 AM - 6 PM), 5% overtime
    ts = generate_timestamp()
    if random.random() < 0.95:
        # Adjust to working hours
        hour = random.randint(9, 18)
        ts = ts.replace(hour=hour)
    
    # 98% chance of home location
    location = user['home_loc'] if random.random() < 0.98 else random.choice(LOCATIONS)
    
    return {
        'event_id': event_id,
        'timestamp': ts,
        'user_id': user_id,
        'user_name': user['name'],
        'department': user['dept'],
        'role': user['role'],
        'source_ip': generate_ip(is_internal=True),
        'location': location,
        'login_successful': True,
        'failed_attempts': random.randint(0, 2),
        'resources_accessed': random.randint(1, 20),
        'sensitive_data_accessed': False,
        'privilege_level': 1,
        'download_mb': random.uniform(0.1, 50.0),
        'session_duration_minutes': random.randint(5, 480),
        'is_anomaly': False,
        'anomaly_type': 'Normal'
    }

def generate_attack_event(event_id):
    attack_type = random.choice([
        'Credential Stuffing',
        'Impossible Travel', 
        'Data Exfiltration',
        'Lateral Movement',
        'After Hours Exfiltration'
    ])
    
    user_id = random.choice(USERS)
    user = USER_DETAILS[user_id]
    ts = generate_timestamp()
    
    event = {
        'event_id': event_id,
        'timestamp': ts,
        'user_id': user_id,
        'user_name': user['name'],
        'department': user['dept'],
        'role': user['role'],
        'source_ip': generate_ip(is_internal=True), # Default, overridden below
        'location': user['home_loc'], # Default
        'login_successful': True,
        'failed_attempts': 0,
        'resources_accessed': random.randint(1, 20),
        'sensitive_data_accessed': False,
        'privilege_level': 1,
        'download_mb': random.uniform(0.1, 50.0),
        'session_duration_minutes': random.randint(5, 60),
        'is_anomaly': True,
        'anomaly_type': attack_type
    }
    
    if attack_type == 'Credential Stuffing':
        event['failed_attempts'] = random.randint(50, 500)
        event['login_successful'] = False
        event['source_ip'] = generate_ip(is_internal=False)
        
    elif attack_type == 'Impossible Travel':
        event['location'] = random.choice(FOREIGN_LOCATIONS)
        event['source_ip'] = generate_ip(is_internal=False)
        event['login_successful'] = True # Successfully compromised
        
    elif attack_type == 'Data Exfiltration':
        event['download_mb'] = random.uniform(500.0, 10000.0)
        event['sensitive_data_accessed'] = True
        
    elif attack_type == 'Lateral Movement':
        event['resources_accessed'] = random.randint(50, 200)
        event['privilege_level'] = 3 # Attempting admin access
        event['failed_attempts'] = random.randint(1, 10)
        
    elif attack_type == 'After Hours Exfiltration':
        # Force night time (1 AM - 4 AM)
        event['timestamp'] = event['timestamp'].replace(hour=random.randint(1, 4))
        event['download_mb'] = random.uniform(200.0, 2000.0)
        event['source_ip'] = generate_ip(is_internal=False)
        event['location'] = random.choice(FOREIGN_LOCATIONS)

    return event

def main():
    print(f"Generating {NUM_EVENTS} events...")
    
    data = []
    for i in range(1, NUM_EVENTS + 1):
        if random.random() < ANOMALY_RATE:
            data.append(generate_attack_event(i))
        else:
            data.append(generate_normal_event(i))
            
    df = pd.DataFrame(data)
    
    # Sort by timestamp
    df = df.sort_values('timestamp')
    
    # Backup existing file
    if os.path.exists(OUTPUT_FILE):
        print(f"Backing up existing {OUTPUT_FILE} to {BACKUP_FILE}...")
        shutil.copy(OUTPUT_FILE, BACKUP_FILE)
        
    # Save new file
    print(f"Saving to {OUTPUT_FILE}...")
    df.to_csv(OUTPUT_FILE, index=False)
    print("Done!")
    print(f"Stats:\nTotal: {len(df)}\nAnomalies: {df['is_anomaly'].sum()}")

if __name__ == '__main__':
    main()
