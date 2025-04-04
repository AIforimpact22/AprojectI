import streamlit as st

def show():
    st.header("1.4 What is in the Python Script?")
    st.write(
        "A Python script combines libraries, variables, functions, and loops to create structured workflows. In a Python script, you’ll find a set of instructions "
        "written in the Python programming language. These instructions, also called code, tell the computer exactly what to do, step by step. "
        "Think of a Python script like a recipe in a cookbook, where each line of code is an instruction for completing part of the overall task."
    )
    st.write("**Importing Libraries:** Often, the script starts by importing libraries. Libraries are collections of pre-built code that allow the script to perform specific tasks—like handling data, creating visuals, or connecting to the internet—without needing to write these functions from scratch.")
    st.write("Example: `import pandas as pd` – this line imports a library for handling data tables.")
    st.write("**Defining Variables:** Variables are like labeled containers that store information, such as numbers or text. These containers hold data that might be needed later in the script.")
    st.write("Example: `temperature = 72` – stores the number 72 in a variable called `temperature`.")
    st.write("**Functions and Loops:** Functions are small, reusable chunks of code that perform specific tasks, while loops are instructions that repeat tasks multiple times. They make your code more efficient and reduce repetition.")
    st.write("Example: `for item in list:` – starts a loop that goes through each item in a list.")
    st.write("**Data Processing and Analysis:** Many scripts work with data—cleaning, calculating, or organizing it to prepare for further analysis.")
    st.write("Example: Cleaning data or calculating averages using built-in functions.")
    st.write("**Output and Visualization:** Finally, scripts often display results to the user by printing text, creating charts, or saving files.")
    st.write("Example: `print(\"The average temperature is:\", average_temp)` displays the result.")
    st.code(
        """
# 1. Importing Libraries
import pandas as pd  # This library helps manage and analyze data in tables
import matplotlib.pyplot as plt  # This library helps create visualizations like charts

# 2. Defining Variables
data = {'Temperature': [70, 75, 80, 85, 90], 'Humidity': [30, 45, 50, 60, 70]}  # Creating sample data
city = "Kurdistan"  # Name of the location for the data

# 3. Creating a DataFrame and Calculating the Average Temperature
df = pd.DataFrame(data)  # Convert the data dictionary into a table
average_temp = df['Temperature'].mean()  # Calculate the average temperature

# 4. Loop through Data to Print Each Temperature
print(f"Weather data for {city}:")
for temp in df['Temperature']:
    print(f"- Temperature: {temp}°F")

# 5. Visualize Data: Plotting Temperature and Humidity
plt.plot(df['Temperature'], label='Temperature', color='red')
plt.plot(df['Humidity'], label='Humidity', color='blue')
plt.xlabel('Day')
plt.ylabel('Value')
plt.title(f"Weather Data for {city}")
plt.legend()
plt.show()

# 6. Output the Result
print(f"The average temperature in {city} is {average_temp}°F.")
        """,
        language="python",
    )

