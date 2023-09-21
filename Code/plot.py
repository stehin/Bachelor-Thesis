# Import Module
from matplotlib import pyplot
import csv

# Intialize empty list
t = []
yPrecision = []
yG1 = []
i = 0

with open('report.csv','r') as csv_file:
  # Read all rows data
  rows = csv.reader(csv_file)

  # Iterate thourgh rows
  for row in rows:
    t.append(i)
    yPrecision.append(float(row[0]))
    yG1.append(float(row[1]))
    i += 1
with open('report_write.csv', 'w') as csv_file:
  write = csv.writer((csv_file))
  for c in range(len(t)):
    write.writerow([t[c], yPrecision[c], yG1[c]])


print(t)
print(yG1)
print(yPrecision)
# Plotting the data
pyplot.plot(t, yPrecision, label="precision=f(t)")
pyplot.plot(t,yG1, label="G1=g(t)")
pyplot.xlabel("andamento del tempo")
pyplot.ylabel("andamento del traffico")
pyplot.legend()

# Display the Plot
pyplot.show()
