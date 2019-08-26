import csv
from random import randint
from sklearn import tree
from sklearn.externals.six import StringIO
import pydot


def timeToMin(inputTimeString):
	hours = int(inputTimeString.split(':')[0])
	mins = int(inputTimeString.split(':')[1])
	totalMins = (hours * 60) + mins

	return totalMins


def createAverage(tripList):
	if len(tripList) == 1:
		return tripList

	SUM = tripList[0]
	for row in tripList[1:]:
		for i, val in enumerate(row):
			SUM[i] = SUM[i] + val

	for i, val in enumerate(SUM):
		SUM[i] = round(SUM[i] / len(tripList), 5)

	return SUM


def getMax(indexToTest, tripList, findMax=True):
	data = {}
	for i, row in enumerate(tripList):
		data[i] = row[indexToTest]

	if findMax:
		return tripList[max(data, key=data.get)]
	elif not findMax:
		return tripList[min(data, key=data.get)]


# FEATURE FUNCTIONS #

def avgPosition(inputList, index=5):
	W_poss = []
	N_poss = []
	for row in inputList:
		W_poss.append(row[index])
		N_poss.append(row[index + 1])
	W_avg = round(sum(W_poss) / len(W_poss), 5)
	N_avg = round(sum(N_poss) / len(N_poss), 5)
	return [W_avg, N_avg]


def totalDist(inputList, index=1):
	total = 0
	for row in inputList:
		total += row[index]
	return total


def avgDist(inputList, index=1):
	total = totalDist(inputList)
	avg = total / len(inputList)

	return round(avg, 3)


def totalDuration(inputList, index=2):
	total = 0
	for row in inputList:
		total += row[index]
	return total


def avgDuration(inputList, index=2):
	total = totalDuration(inputList)
	avg = total / len(inputList)

	return avg


def longestDist(inputList, index=1):
	allDists = []
	for row in inputList:
		allDists.append(row[index])

	return max(allDists)


# POSITIONAL BINARIES #

def been_pos(inputList, mins, maxs, index=5):
	all_poss = []
	for i, row in enumerate(inputList):
		point = (row[index + 1], row[index])

		x_good = point[0] > mins[0] and point[0] < maxs[0]
		y_good = point[1] > mins[1] and point[1] < maxs[1]

		if x_good and y_good:
			return True
		else:
			pass
			# return (False, point, (x_good, y_good))
	return False


def been_church(inputList, index=5):
	Mins = (31.239, -85.437)
	Maxs = (31.241, -85.435)
	return been_pos(inputList, Mins, Maxs)


def been_nview(inputList, index=5):
	Mins = (31.266, -85.385)
	Maxs = (31.272, -85.375)
	return been_pos(inputList, Mins, Maxs)


def been_wallace(inputList, index=5):
	Mins = (31.310, -85.475)
	Maxs = (31.320, -85.465)
	return been_pos(inputList, Mins, Maxs)


def been_home(inputList, index=5):
	Mins = (31.249, -85.438)
	Maxs = (31.251, -85.436)
	return been_pos(inputList, Mins, Maxs)


# POSITIONAL EXTREMES #

def WMax(inputList, index=5):
	W_poss = []
	for row in inputList:
		W_poss.append(row[index])
	return min(W_poss)


def EMax(inputList, index=5):
	W_poss = []
	for row in inputList:
		W_poss.append(row[index])
	return max(W_poss)


def NMax(inputList, index=6):
	N_poss = []
	for row in inputList:
		N_poss.append(row[index])
	return max(N_poss)


def SMax(inputList, index=6):
	N_poss = []
	for row in inputList:
		N_poss.append(row[index])
	return min(N_poss)


# HOULY BINARIES #

def makeHourlyBinaries(inputList, index=0):
	times = []
	for row in inputList:
		times.append(int(row[index] / 60))

	output = []
	for i in range(24):
		output.append(i in times)
	return output


'''#################################################################'''
'''  SETTINGS  '''
SAMPLE_SIZE = 60
FULL_OUTPUT = False
'''#################################################################'''

# DATA FORMATTING #
# LOAD DATA #
filePATH = "data_to_April.csv"

rows = []
with open(filePATH) as file:
	csvreader = csv.reader(file)

	for row in csvreader:
		rows.append(row)

Titles = rows.pop(0)

data = [x[2:] for x in rows]
dates = [x[1] for x in rows]
answers = [x[0] for x in rows]
correctData = []

# CONVERT TIME FROM STRING #
for row in data:
	startTimeAsMins = 5 * (timeToMin(row[0]) / 5)
	distance = float(row[1])
	durationTimeAsMins = 5 * (timeToMin(row[2]) / 5)
	coords = [float(x) for x in row[3:]]

	newRow = [startTimeAsMins, distance, durationTimeAsMins] + coords
	correctData.append(newRow)

# GROUP BY DAYS #
daySorted = []
lastDate = dates[0]
day = []
for i, row in enumerate(correctData):
	if len(row) < 1:
		pass
	else:
		if dates[i] == lastDate:
			day.append(row)
		else:
			daySorted.append([answers[i - 1], day])
			lastDate = dates[i]
			day = []


# FEATURE CREATION #
featureAnswers = []
featureData = []
for i, day in enumerate(daySorted):
	sample = day[1]

	if len(sample) < 1:
		print(f"Skipping Day {i} for zero data")
	else:

		durations = avgPosition(sample) + [totalDist(sample)] + [avgDist(sample)] + [totalDuration(sample)] + [avgDuration(sample)] + [longestDist(sample)]
		cardinal_extremes = [WMax(sample)] + [EMax(sample)] + [NMax(sample)] + [SMax(sample)]
		keypoints = [been_church(sample)] + [been_nview(sample)] + [been_wallace(sample)] + [been_home(sample)]
		time_binaries = makeHourlyBinaries(sample)

		FULL_LINE = durations + cardinal_extremes + keypoints + time_binaries

		featureData.append(FULL_LINE)

		answer = day[0]

		if answer in ["Monday", "Tuesday", "Thursday"]:
			featureAnswers.append("Mon-Thu")
		else:
			featureAnswers.append(answer)


# SELECT DATA FOR TREE #
answers = featureAnswers
correctData = featureData


# PULL TEST DATA #
print(f"Len of data before testSelections: {len(correctData)}")
testData = []
for i in range(SAMPLE_SIZE):
	selection = randint(0, len(correctData) - 1)
	data = correctData.pop(selection)
	answer = answers.pop(selection)

	DICT = {"correct": answer, "data": data, "index": selection}
	testData.append(DICT)
print(f"Len of data after testSelections: {len(correctData)}")


# MODEL FORMATION #
clf = tree.DecisionTreeClassifier()
dayPredictor = clf.fit(correctData, answers)


# MODEL TESTING #
print("\n\tSTARTING TESTS: ")
count = 0
dayCounts = {"Sunday": 0, "Mon-Thu": 0, "Monday": 0, "Tuesday": 0, "Wednesday": 0, "Thursday": 0, "Friday": 0, "Saturday": 0}
dayTotals = {"Sunday": 0, "Mon-Thu": 0, "Monday": 0, "Tuesday": 0, "Wednesday": 0, "Thursday": 0, "Friday": 0, "Saturday": 0}
for sample in testData:
	modelPrediction = dayPredictor.predict([sample["data"]])[0]
	correctAnswer = sample["correct"]
	ind = sample["index"]

	if modelPrediction != correctAnswer:
		if FULL_OUTPUT:
			print(f"{ind} \tPrediction: {modelPrediction} {' '*(10 - len(modelPrediction[0]))} Correct: {correctAnswer}")
		pass
	else:
		count += 1
		dayCounts[modelPrediction] += 1
		if FULL_OUTPUT:
			print(f"{ind} \tPrediction: {modelPrediction} {' '*(10 - len(modelPrediction[0]))} Correct: {correctAnswer}   |   CORRECT ANSWER !!!")

	dayTotals[correctAnswer] += 1

print(f"\n\tTotal Correct: {count}/{len(testData)} ({round((count/len(testData))*100, 2)}%)  \n")
for day in dayCounts:
	if dayTotals[day] != 0:
		print(f"{day}: \t{dayCounts[day]}/{dayTotals[day]} \t({round((dayCounts[day]/dayTotals[day])*100, 1)}%)")
print("")


# VISUALIZATION #

if input("Make model tree? (y/N): ").lower() == 'y':
	print("\n\tSTARTING GRAPH")
	FEATURES = ['Average_Position_X', 'Average_Position_Y',
	'Total_Distance', 'Average_Distance', 'Total_Duration',
	'Average_Duration', 'Longest_Dist', 'WMax', 'EMax', 'NMax',
	'SMax', 'Church-bin', 'NView-bin', 'Wallace-bin', 'Home-bin',
	'0-HourBin', '1-HourBin', '2-HourBin', '3-HourBin', '4-HourBin',
	'5-HourBin', '6-HourBin', '7-HourBin', '8-HourBin', '9-HourBin',
	'10-HourBin', '11-HourBin', '12-HourBin', '13-HourBin', '14-HourBin',
	'15-HourBin', '16-HourBin', '17-HourBin', '18-HourBin', '19-HourBin',
	'20-HourBin', '21-HourBin', '22-HourBin', '23-HourBin']

	DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
	ABBREVIATED_DAYS = ["Sunday", "Mon-Thu", "Wednesday", "Friday", "Saturday"]
	dot_data = StringIO()
	tree.export_graphviz(
		clf, out_file=dot_data, filled=True, rounded=True, impurity=True,
		class_names=ABBREVIATED_DAYS,
		rotate=True,
		feature_names=FEATURES)

	graph = pydot.graph_from_dot_data(dot_data.getvalue())
	graph = graph[0]
	graph.write_pdf("tree_model.pdf")

	print("\n\t~~~FINISHED GRAPH~~~")
	print("\tSaved as tree_model.pdf")
