import pandas as pd
import sys
import math
from tokenize import group
from collections import defaultdict

def close_enough(t1, t2):
    if math.isclose(t1[0], t2[0], abs_tol = 0.005) and math.isclose(t1[1], t2[1], abs_tol=0.05):
        return True
    else:
        return False
    
# create output name
filename=sys.argv[1]
filename = filename[:-5]
outputname_main=filename+"_condensed.csv"
outputname_secondary=filename+"_condensed_secondary.csv"

#Create empty tables for main and secondary information
subtables=pd.DataFrame()
maintable=pd.DataFrame()

# Read file
metab_df=pd.read_excel(sys.argv[1])

# Initialize empty columns
metab_df['NumberCol']=""
metab_df['Type']=""
n=0

# Loop to create groupings of secondary tables
for index, row in metab_df.iterrows():
    if isinstance(row['m/z'], (float,int)):
        metab_df.at[index, 'Type']= "Main" 
        metab_df.at[index, 'NumberCol']=n 
        n+=1
    else:
        metab_df.at[index, 'NumberCol']= n -1
        metab_df.at[index, 'Type']= "Secondary" 

print("Out of loop")

#seperate main and secondary tables
maintable=metab_df[metab_df['Type']=="Main"] 
subtables=metab_df[metab_df['Type']=="Secondary"] 

# Get ordering of columns
all_colnames=list(metab_df.columns.values)
all_colnames.append("m/z round")
all_colnames.append("Annot. DeltaMass [Da] round")

#Process main table information
#maintable = maintable[maintable['mzVault Best Match'] > 0] 
maintable['m/z'] = maintable['m/z'].astype(float)
maintable['m/z round']=maintable['m/z'].round(decimals = 3)
maintable['Annot. DeltaMass [Da]'] = maintable['Annot. DeltaMass [Da]'].astype(float)
maintable['Annot. DeltaMass [Da]'] = maintable['Annot. DeltaMass [Da]'].fillna(0)
maintable['Annot. DeltaMass [Da] round']=maintable['Annot. DeltaMass [Da]'].round(decimals = 2)

#Create dictionary for aggregation function
colNames = maintable.columns[maintable.columns.str.contains(pat = 'Area:')] 
d1 = dict.fromkeys(colNames, 'sum')
d = {'Area (Max.)':"first",**d1}

#aggregate main table information
metab_data_col =maintable.drop(columns=list(colNames))
metab_agg = maintable.groupby(['m/z round', 'Annot. DeltaMass [Da] round'], as_index=False).aggregate(d)
print("Grouped")
# Add in other columns and reindex order
metab_agg_wdescp = pd.merge(metab_agg, metab_data_col,  how='left', left_on=['m/z round', 'Annot. DeltaMass [Da] round','Area (Max.)'], right_on = ['m/z round', 'Annot. DeltaMass [Da] round','Area (Max.)'])
metab_agg_wdescp = metab_agg_wdescp.reindex(columns=all_colnames)
print("Merged")

#Wobble functiono on aggregate table
groupby_num = 0
dict_groupby = defaultdict(list)

dict_info = dict([(i,[x,y]) for i,x,y in zip(metab_agg_wdescp['NumberCol'], metab_agg_wdescp['m/z round'],metab_agg_wdescp['Annot. DeltaMass [Da] round'])])

while True:
    list_to_remove = []
    if not dict_info:
        break
    
    for key1 in dict_info:
        dict_groupby[groupby_num].append(key1)
        for key2 in dict_info:
            if key1 == key2:
                pass
            else:
                if close_enough(dict_info[key1], dict_info[key2]):
                    dict_groupby[groupby_num].append(key2)
                else:
                    pass
        list_to_remove = dict_groupby[groupby_num]
        groupby_num += 1
        break
    for item in list_to_remove:
        dict_info.pop(item)
                    
grouby_dataframe = pd.DataFrame()

for key, value in dict_groupby.items():
    for item in value:
        temp = pd.DataFrame(
            {
            'GroupbyNum': key,
            'NumberCol': value
            }
        )

        grouby_dataframe = pd.concat([grouby_dataframe, temp])

metab_withgroupby = pd.merge(metab_agg_wdescp, grouby_dataframe,  how='left', left_on=['NumberCol'], right_on = ['NumberCol'])

colNames = metab_agg_wdescp.columns[metab_agg_wdescp.columns.str.contains(pat = 'Area:')] 
d1 = dict.fromkeys(colNames, 'sum')
d = {**d1}

#aggregate main table information
main_noabund =metab_withgroupby.drop(columns=list(colNames))
main_wobble_agg = metab_withgroupby.groupby(['GroupbyNum'], as_index=False).aggregate(d)
main_noabund.drop_duplicates(subset="GroupbyNum", inplace=True)
main_wobble_withdescp = pd.merge(main_wobble_agg, main_noabund,  how='left', left_on=['GroupbyNum'], right_on = ['GroupbyNum'])
main_wobble_withdescp =main_wobble_withdescp.drop(columns="GroupbyNum")
main_wobble_withdescp = main_wobble_withdescp.reindex(columns=all_colnames)
# Ouput main table only
main_wobble_withdescp.to_csv(outputname_main, index=False)  
print("Wobble")
#remove secondary table entries not found in main table
subtables_reduced=subtables[subtables["NumberCol"].isin(main_wobble_withdescp["NumberCol"])]
subtables_reduced=subtables_reduced.reindex(columns=all_colnames)

#Merge with main table and sort
all_data=pd.concat([main_wobble_withdescp, subtables_reduced])
all_data_sorted=all_data.sort_values(by = ['NumberCol', 'Type'], ascending = [True, True])
print("Secondary")
#Output table with secondary information
all_data_sorted.to_csv(outputname_secondary, index=False)  

