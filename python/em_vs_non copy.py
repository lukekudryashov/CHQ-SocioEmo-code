# separates raw data into emotional and non-emotional needs questions, writes each into a separate csv

import pandas as pd
import csv, math, ast, json, re
import numpy as np

def join_dfs_from_files(*arg):
	"""
	takes any number of strings (file names, include '.csv')
	reads each file as pandas df, joins all dfs into one
	returns the combined dfs
	"""
	df = pd.DataFrame()

	for file_name in arg:
		#read data file
		with open(file_name) as csvfile:
			new_df = pd.read_csv(csvfile)
		
		#check if df has already been filled with the first dataframe
		if df.empty:
			df = new_df
			#print("df is empty")
		else:
			df = pd.concat([df, new_df], axis=0)
			#print("df is not empty")

	return df


def separate(df):
	"""
	takes a pandas df (df)
	separates into two dfs - one that has emotional needs questions (alone or with others), the other that has any needs except emotional
	writes dfs to csvs
	"""

	nonem_df = pd.DataFrame()
	em_df = pd.DataFrame()

	#iterate over each row in the combined df
	em_count = 0
	nonem_count = 0
	for index, row in df.iterrows():
		#takes the value of the informational_support column in that row
		em_support = row['emotional_support']
		#checks if the value is nan (type is string if there is content, float if there is not)
		if(type(em_support) == float):
			nonem_count += 1
			#adds the row to the noninf df if informational_support column is empty
			nonem_df = nonem_df.append(row)
		else:
			#adds the row to the inf df if informational_support column is not empty
			em_df = em_df.append(row)
			em_count += 1
	print(em_count)
	print(nonem_count)

	#writes the dfs to csvs
	nonem_df.to_csv('nonem.csv')
	em_df.to_csv('em.csv')


	


df = join_dfs_from_files('Ann_AlL.csv')
print(len(df))
separate(df)