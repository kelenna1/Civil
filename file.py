import pandas as pd

# Sample data
data = {
    'name': ['Jon Snow', 'Harvey Specter', 'Barry Allen', 'Richard Mill', 'The Professor'],
    'date_of_birth': ['1995-08-15', '1998-03-22', '1990-11-05', '1993-07-30', '1997-01-18']
}

# Create DataFrame
df = pd.DataFrame(data)

# Save to files
df.to_excel('sample_birthdays.xlsx', index=False)
df.to_csv('sample_birthdays.csv', index=False)