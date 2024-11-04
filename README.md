# Metabolite-Condensing-Script
A script to condense the ouput from compound discoverer by m/z and annotated delta mass by summing areas of peaks that are the same within a sample.

The input of this script is an excel file generated from the program compound discoverer. In compound discoverer, you can output the main file with or without secondary information. The script can handle the secondary information but you must ensure that the secondary information contains text in the 'm/z' column. The output is two csv files labeled "_condensed.csv" containing only the main table and "_condensed_secondary.csv" which contains both the main and secondary information. Currently the script allows for m/z to be within +/- 0.005 and annotated delta mass to be within +/- 0.05 for them to be considered the same metabolite and summed. 

An example compound discoverer, output and secondary output file are provided. 
