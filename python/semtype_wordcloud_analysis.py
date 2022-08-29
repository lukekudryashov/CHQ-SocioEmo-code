### this program produces a csv of semtype counts for all concepts in the data for each field from the raw data

from pymetamap import MetaMapLite
import pandas as pd
import csv, math, ast, json, re

#set up MetaMapLite instance
mm = MetaMapLite.get_instance('/Users/luke/Desktop/metamap/public_mm_lite')

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


def extract_concepts_from_field(field, df):
	"""
	takes a string (field) and a pandas dataframe (df). field must be a column name present in the dataframe.
	extracts concepts from each cell in the corresponding df column,
	returns list of dictionaries matching cuis of extracted concepts to their semtypes
	"""

	print(f"started {field}")

	#check if field is a valid column in df, exit function if not
	if field not in df:
		print(f"{field} is not a column in the dataframe")
		return df
	#create a list of just the field column
	field_df = df[field]

	#lists to be filled with extracted concept info
	concept_list = []

	#extract cui for the concepts in each cell in the field column
	for entry in field_df:
		#check that the cell actually has string content (otherwise 'nan' values get read as a string)
		if type(entry) == str:
			sents = [entry]
			concepts,error = mm.extract_concepts(sents)
			for concept in concepts:
				concept_dict = dict.fromkeys(['cui','semtypes'])
				concept_dict['cui'] = concept.cui
				string_no_punctuation = re.sub("[^\w\s]", "", concept.semtypes)
				semtype_list = string_no_punctuation.split()
				concept_dict['semtypes'] = semtype_list
				concept_list.append(concept_dict)
				print(concept.cui)

	#add cuis and names of extracted concepts as columns to df
	return concept_list

def run_extraction_on_df(df):
	"""
	takes a pandas dataframe (df)
	runs extract_concepts_from_field on focus and emotion cause columns in df
	returns updated df
	writes the updated df to the file_name provided appended with "_with_concepts".
	"""

	#extract concepts, add each returned dict list to a new variable
	print(f"started extraction")
	focus_concepts = extract_concepts_from_field('focus', df)
	print(f"finished focus")
	sadness_concepts = extract_concepts_from_field('sadness_cause', df)
	print(f"finished sadness")
	joy_concepts = extract_concepts_from_field('joy_cause', df)
	print(f"finished joy")	
	fear_concepts = extract_concepts_from_field('fear_cause', df)
	print(f"finished fear")	
	anger_concepts = extract_concepts_from_field('anger_cause', df)
	print(f"finished anger")	
	surprise_concepts = extract_concepts_from_field('surprise_cause', df)
	print(f"finished surprise")	
	disgust_concepts = extract_concepts_from_field('disgust_cause', df)
	print(f"finished disgust")	
	trust_concepts = extract_concepts_from_field('trust_cause', df)
	print(f"finished trust")	
	anticipation_concepts = extract_concepts_from_field('anticipation_cause', df)
	print(f"finished anticipation")	
	confusion_concepts = extract_concepts_from_field('confusion_cause', df)
	print(f"finished confusion")
	denial_concepts = extract_concepts_from_field('denial_cause', df)
	print(f"finished denial")
	#combine all the emotion cause concept lists into one
	emotion_concepts = sadness_concepts + joy_concepts + fear_concepts + anger_concepts + surprise_concepts + disgust_concepts + trust_concepts + anticipation_concepts + confusion_concepts + denial_concepts

	#read the sem type and sem group codes from text files into a dataframe
	semtype_df = pd.read_csv('SemanticTypes_2018AB.txt', sep='|', header=None, names=['semtype_code','semtype_num','semtype_name'])
	print(semtype_df)
	semgroup_df = pd.read_csv('SemGroups_2018.txt',sep='|',header=None,names=['group_code','group_name','semtype_num','semtype_name'])
	print(semgroup_df)
	semtype_df = pd.merge(semtype_df, semgroup_df, on=['semtype_num','semtype_name'], how='outer')
	print(semtype_df)

	column_names = ['_focus','_emotion','_sadness', '_joy','_fear','_anger','_surprise', '_disgust', '_trust', '_anticipation', '_confusion', '_denial']
	column_count = 0

	#list of semtypes that are of interest
	selected_semtypes = ['cgab','acab','inpo','patf','dsyn','anab','neop','mobd','sosy','bact','fndg','hops','inbe','topp','lbpr','diap','ftcn','hlca','medd','clnd','antb','phsu','nsba','strd','vita','aapp','bdsy','bpoc','tisu','blor','bsoj','bdsu','orga','inpr','qlco','tmco','idcn','spco','cnce','mnob','food','sbst','clna','menp','orgf','ortf','phsf','bodm','horm','popg','prog','famg','virs','aggp','podg','humn','bmod','acty','socb','ocac','dora','bhvr','npop','phpr','anst','hrco','orgt']

	#remove all but selected semtypes from semtype_df
	semtype_df = semtype_df[semtype_df['semtype_code'].isin(selected_semtypes)]
	
	for cat in [focus_concepts, emotion_concepts, sadness_concepts, joy_concepts, fear_concepts, anger_concepts, surprise_concepts, disgust_concepts, trust_concepts, anticipation_concepts, confusion_concepts, denial_concepts]:
		#for each list of concept/ semtype dicts, create a new dict counting the number of types each semtype of interest appears (repeat cuis also counted)
		semtype_dict = dict()
		for concept_dict in cat:
			for semtype in concept_dict['semtypes']:
				if semtype in selected_semtypes:
					if semtype in semtype_dict:
						semtype_dict[semtype] += 1
					else:
						semtype_dict[semtype] = 1
		
		semtype_counts = []
		for key,value in semtype_dict.items():
			semtype_counts.append({'semtype_code':key, 'count': value})
		print(semtype_dict)
		print(semtype_counts)

		#create a new dataframe of semtype counts for each category
		new_df = pd.DataFrame(semtype_counts)
		print(new_df)
		semtype_df = pd.merge(semtype_df, new_df, on='semtype_code',how='outer',suffixes=[None,column_names[column_count]])
		column_count += 1
		print(semtype_df)

	#write the semtype count df to a csv file
	semtype_df.to_csv('semtype_counts.csv')
	#return semtype_df

	print(f"extraction complete")


#runs the code on specified data files
df = join_dfs_from_files('Ann_AlL.csv')
#df1 = join_dfs_from_files('em.csv')
#df2 = join_dfs_from_files('nonem.csv')

run_extraction_on_df(df)

#run_extraction_on_df(df1).to_csv('semtype_counts_em.csv')
#un_extraction_on_df(df2).to_csv('semtype_counts_nonem.csv')
#print(df)


