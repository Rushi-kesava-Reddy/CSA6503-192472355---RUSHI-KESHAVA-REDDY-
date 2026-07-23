import pandas as pd

data = {
    "Name": ["Hari", "Ram", "John"],
    "Age": [20, 21, 22],
    "Marks": [90, 85, 95]
}

df = pd.DataFrame(data)

print(df["Name"])
print(df[["Name", "Marks"]])