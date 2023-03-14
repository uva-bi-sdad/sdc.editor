# sdc.editor

This repo provides automated edits for miscellaneous tasks. The editor is expected to perform edits in the following sequence:

1. *Create ```manifest.json```*: loops through all folders that match ```**/distribution/``` and creates a ```manifest.json``` at the root directory with the: hash, file size (bytes), and file path of each file.
2. *Auto generate directory structures*: if ```**/distribution``` is found, the editor additionally creates `code`, `data`, and `docs` 
3. *Create a placeholder `measure_info.json` files*: for each file added, 
4. *Update structure of existing `measure_info.json` files*: using a template (`measure_info_template.json`) stored in this repository. Meaning:
    - Create a new key and fill it with '' when required keys as specificed by templates are not found
    - Search for ```*.csv.xz``` in the same directory, and check for a string match of the measure and the file name. If there is a match, appends the new measures into the ```measure_info.json```