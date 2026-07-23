import pandas as pd

data = {
    "Name": ["Hari", "Ram", "John"],
    "Marks": [90, 85, 95]
}

df = pd.DataFrame(data)

print("Average Marks:", df["Marks"].mean())