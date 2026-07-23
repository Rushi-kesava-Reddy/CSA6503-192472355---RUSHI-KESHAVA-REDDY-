import matplotlib.pyplot as plt

labels = ["Python", "Java", "C++"]
sizes = [45, 35, 20]

plt.pie(sizes, labels=labels, autopct="%1.1f%%")

plt.show()