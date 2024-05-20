---
title: "Itemmaster upload script"
linkTitle: "Itemmaster upload"
weight: 2
description: >-
    How to use itemmaster upload script
---

**This scripts is using to speed up the itemmaster upload process**

During release qualification it is needed to check itemmaster upload functionality. 
This script can be used for any purposes, where is needed to upload itemmaster. 
It is working for any retailer.
To run this script:
1. Do all the steps from "Release qual tool setup"
2. To run the script, execute in terminal
```bash
python3 -m scripts.itemmaster_upload <retailer> <env> <location-code-tom>
```
* Also it is possible to run without indicating retailer, env and location-code-tom. In this case, on the screen will appear hint, that you need to enter all needed information
* Depends on the retailer, the upload mode is selected (GCP or FTP).
3. On the screen will appear hints, what you need to do next. To upload the file, it is needed to enter the absolute path to file.
* It is meaning that you need to enter the path in the format:
```bash
/User/folder_where_file_is_places/itemmaster_file.file_extention
```
4. After you've entered the absolute path to file, itemmaster will upload file to needed place, and will wait until the file processed, and information updated in distiller.
