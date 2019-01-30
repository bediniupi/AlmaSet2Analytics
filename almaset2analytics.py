#!/bin/python
# -*- coding: UTF-8 -*-
#
#almaset2analytics.py
# 2019 by Nazzareno Bedini, University of Pisa
import sys
import re
import argparse

# ini section: configure it only if you want to use APIs to get sets
# Configuration and Administration API
apiServer = 'https://api-eu.hosted.exlibrisgroup.com'
apiSetKey = 'yourInstitutionKey' 
# end ini section

#return a xml object from web api
def get_xmlobj(api_url, qp):
    try:
        response = requests.get(api_url, params=qp)       
    except requests.exceptions.RequestException as e:  
        print ("Error on api get info, please check you connection and retry:\n" + str(e))
        print ("Url:\n" + response.url)
        exit()
    response_obj = etree.fromstring(response.content)
    return response_obj, response.url, response.content

# parsing line command arguments
usage_example = '''example:
    
    python almaset2analytics analysis.xml -s 123456789 -o analysis_modified.xml (get data from Alma set id 123456789 and write the output to anaysis_modified.xml)
    python almaset2analytics analysis.xml -s 123456789 -o -d analysis_modified.xml (same as above, but read the data from set in description instead of in id)
    
    python almaset2analytics analysis.xml -f data.csv -c "MMS ID" -o analysis_modified.xml (read the data from the column MMS ID of data.csv file)
    python almaset2analytics analysis.xml -f data.csv -c "MMS ID"  (same as above, but the output overwrite analysis.xml file)'''

parser = argparse.ArgumentParser(description='Use an Alma set or other list of data in csv file as basis for Analytic analysis, \nmodifing an exported file with the analysis in XML format adding a IN filter with the data collected.\nRemember to set a filter "is Prompted" in Analytics to the column you want to convert.',
                                epilog=usage_example,
                                formatter_class=argparse.RawDescriptionHelpFormatter)

parser.add_argument('analysis', metavar='file_analysis.xml', help='Origin file xml of the analysis, obtained coping and paste the analysis XML in Advanced tab')
parser.add_argument('-s', '--set', metavar='Alma Set ID', action='store', dest='s', help='ID number of Alma set (require Configuration and Administration API access and key configurated in the INI section of the script)')
parser.add_argument('-d', '--description', action="store_true", default=False, dest='d', help='Collect description from Alma set by API instead of id')
parser.add_argument('-f', '--file', metavar='filename.csv', action='store', dest='f', help='CSV file input to collect data')
parser.add_argument('-c', '--column', metavar='ColumnName', action='store', dest='c', help='Column of CSV file to collect data')
parser.add_argument('-o', '--output', metavar='filename.xml', action='store', dest='o', help='XML file to write the changed analysis (if missed the input xml file will be overwritten')

args = parser.parse_args()

filename_xml = args.analysis
filename_csv = args.f
if filename_csv:
    retrieve_set_from = 'csv'
    field_csv = args.c
    if not field_csv:
        sys.exit("Error, missing -c argument with column name of csv file")
else:
    set_id = args.s
    if set_id:    
        retrieve_set_from = 'api'
    else:
        sys.exit("Error, you must give -f or -s argument to collect data from file csv or Alma set")
set_tag='id'
if args.d:
    set_tag='description'
output_xml = filename_xml
if args.o:
    output_xml = args.o

# filter xml boundaries
sawx_start = '<sawx:expr xsi:type="sawx:sqlExpression">'
sawx_end = '</sawx:expr>'

# split xml analysis in start - filter prompted - end
prompted_string = ''
analysis_xml_start = ''
analysis_xml_end = ''
prompted_found = False

# read analysis file and extract the prompted column
print ("Reading analysis in file " + filename_xml)
try:
    with open(filename_xml, 'r') as origin:
        for line in origin:
            if "prompted" in line:
                prompted_string += line
                while True:
                    nextLine = next(origin)
                    prompted_string += nextLine
                    if sawx_end in nextLine:
                        prompted_found = True
                        break
            else:
                if prompted_found:
                    analysis_xml_end += line
                else:
                    analysis_xml_start += line
except:
    sys.exit("Error, " + filename_xml + " not found.")
col_search = re.search(sawx_start + '([^<\/]*)(.*)', prompted_string)
try:
    column_name = col_search.group(1)
except:
    sys.exit("Error: no filter prompted found in " + filename_xml)

#clean end of filter
end_prompted_string = col_search.group(2).replace(sawx_end, '', 1)

print ("Filter prompted found on field: " + column_name)
filter_xml_header = '<sawx:expr xsi:type="sawx:list" op="in">\n<sawx:expr xsi:type="sawx:sqlExpression">' + column_name + sawx_end
filter_rows = ''

# retrieve set from csv file
# options -f [file.csv] -c [csv column name])
if retrieve_set_from == 'csv':
    import csv
    filter_rows = ''
    print ("Reading set file csv " + filename_csv)
    try:
        with open(filename_csv) as csv_file:
            csv_ray = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for csv_row in csv_ray:
                if line_count == 0:
                    try:
                        key_field = csv_row.index(field_csv)
                    except:
                        sys.exit("Error: field " + field_csv + " not found in file " + filename_csv)
                        exit()
                    line_count += 1
                else:                    
                    #row in xml filter
                    filter_rows += '<sawx:expr xsi:type="xsd:string">' + csv_row[key_field] + '</sawx:expr>\n'
                    line_count += 1
    except:
        sys.exit("Error, file " + filename_csv + " not found")    
    print ("Found " + str(line_count) + " values in " + filename_csv + " file" )
    print ("Collecting data in column " + field_csv)

# retrieve set from API (need configuration in INI section)
# option: -s [id set] : read id values
# options: -s [id_set] -d : read description values
if retrieve_set_from == 'api':
    import requests    
    from lxml import etree
    print ("Reading set id " + set_id + " from API")
    print ("Retrieve data from " + set_tag + " tag")
    urlSetRetrieve = apiServer + '/almaws/v1/conf/sets/' + set_id + '/members'
    # ricordarsi l'offset
    offset = 0
    queryParams = {'offset': offset, 'limit': 1, 'apikey': apiSetKey, 'set_id': set_id}
    set_obj, url_api, response_xml = get_xmlobj(urlSetRetrieve, queryParams)
    #recupera l'offset
    try:
        total_members = set_obj.attrib['total_record_count']
    except:
        print ("\nError: set not retrieved correctly, check set id provided, your api server and api key;")
        print ("API Url: " + url_api)
        print ("Response from API:")
        print (response_xml)
        exit()
    
    steps = int(int(total_members)/100)+1    
    print ("Found " + total_members + " values, reading in " + str(steps) + " step/s" )
    for step in range(steps):
        print ("Step " + str(step+1) + " of " + str(steps))
        offset = (step*100)
        last_offset = offset+99
        if last_offset>int(total_members):
            last_offset=int(total_members)
        print ("Retrieving members from " + str(offset) + " to " +str(last_offset)         )
        queryParams = {'offset': offset, 'limit': 100, 'apikey': apiSetKey, 'set_id': set_id}
        set_obj, url_api, response_xml = get_xmlobj(urlSetRetrieve, queryParams)
        for row in set_obj.iter():
            if row.tag == set_tag:
                filter_rows += '<sawx:expr xsi:type="xsd:string">' + row.text + '</sawx:expr>\n'

# the filter "is equal to / is in" with all data collected
filter_xml = filter_xml_header + "\n" + filter_rows + "\n" + end_prompted_string

# write the new anaylisis into file
# option: -o [new_file.xml] : write to new_file_xml, otherwise overwrite the input analysis xml file
filedata = analysis_xml_start + filter_xml + analysis_xml_end
with open(output_xml, "w") as output_file:
    output_file.write(filedata)
print ("\nDone: output written in file " + output_xml)
print ("Open the file, select all, then copy and paste in advance xml box in Analytics")
