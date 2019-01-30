# Alma-AlmaSet2Analytics

Use an Alma set or other list of data in csv file as basis for Analytics analysis, modifing an exported file with the analysis in XML format adding a IN filter with the data collected.
Remember to set a filter "is Prompted" in Analytics to the column you want to convert.

## Usage
command: 
```
python almaset2analytics.py [-h] [-s Alma Set ID] [-d] [-f filename.csv]
                            [-c ColumnName] [-o filename.xml]
                            file_analysis.xml

```
## How to use the script (Examples and variations)

1. to obtain the file_analysis.xml create/modify an analysis adding a filter "is prompted" to the column you want to use (if you want you can add others filters, but only one can be "is prompted" type), then go to the "Advanced" tab and copy all xml data in the "Analysis XML" box. Past it into a text file and save it as "file_analysis.xml" or the name you prefer in the same directory of the script
2. create a set in Alma and copy the set id (example id: 221133)
3. invoke the command: 

```
python almaset2analytics.py -s 221133 file_analysis.xml -o analysis_modified.xml
```

4. In Analytics, go to the analysis created (or create a new empty one if you prefer), go to the "Advanced" tab and delete all the content in the "Analysis XML" box
5. Open the file analysis_modified.xml and select all and copy, the past it into the "Analysis XML" box
6. Click on "Apply XML": now the Analysis contain a IN filter with all data collected from set: it is tested for over 40000 items.

Note: the set is retrieved by Configuration and Administration API  retrieve set members, so you have to obtain and add your institutional api key into the INI section of the script

### Variation a
The set data are collected from ID tag, if you want to collect data from Description tag you have to use the -d argument:

3a. invoke the command: 

```
python almaset2analytics.py -s 221133 file_analysis.xml -o analysis_modified.xml -d
```

### Variation b

2b. Export data into a csv file with header; save it into the same directory of the script (ex., data.csv) and copy the header of the column you want collect data from (ex., "MMS ID")

3b. invoke the command: 

```
python almaset2analytics.py -f data.csv -c "MMS ID" file_analysis.xml -o analysis_modified.xml
```
    
Note: if you have a lot of data in the set it's better and faster to use a csv file instead of API retrieve set members method.

### Variation c

3c. if you invoke the command without the -o argument the origin xml file will be overwritten:
    
```
python almaset2analytics.py -f data.csv -c "MMS ID" file_analysis.xml
```
    
5c. Open the file file_analysis.xml and select all and copy, the past it into the "Analysis XML" box

## Installation
No installation needed, simply download allmaset2analytics.py in a rw directory.

## Prerequisites
* Python v3 with modules: requests, lxml, argparse, re, csv
* Alma Ex Libris
* Analytics (OBIEE)
* Configuration and Administration API access and key (not needed if you use csv file as data origin)

## Authors
* **Nazzareno Bedini - University of Pisa**

## Why not use Analytics API methods to export Analysis?
In order to avoid the copy/past actions on the Analytics XML tab I've tried to use the Analytics API methods: unfortunally it's not simple to transfer a lot of data via get method, and also splitting the API query calls is not a viable way, I obtained a lot of timeout errors.

## Acknowledgments
* [Alma API Retrieve Set Members](https://developers.exlibrisgroup.com/alma/apis/docs/conf/R0VUIC9hbG1hd3MvdjEvY29uZi9zZXRzL3tzZXRfaWR9L21lbWJlcnM=/)
* [Rest Members](https://developers.exlibrisgroup.com/alma/apis/docs/xsd/rest_members.xsd/?tags=GET)
* [Working with Analytics REST APIs](https://developers.exlibrisgroup.com/blog/Working-with-Analytics-REST-APIs/)
* [General info to start to works with Alma's APIs](https://developers.exlibrisgroup.com/alma/apis)
