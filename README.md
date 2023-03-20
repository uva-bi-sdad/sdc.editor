# sdc.editor

This repo provides automated edits for miscellaneous tasks maintaining data repositories. The editor is expected to perform edits in the following sequence:

1. **Auto generate directory structures**:
    - If `code`, `data`, or `docs` folder is found, look in it for a `distribution` folder
    - If the `distribution` folder underneath `code`, `data`, or `docs` is empty, auto generates an empty `temp` file
2. **Create a placeholder `measure_info.json` files**: 
    - Loop through each `**/distribution/`. If a `*.csv.xz` is found, but a `measure_info.json` was not found in the same directory, create an empty placeholder `measure_info_temp.json`
    - If a `measure_info.json` is found but is empty, rename it to `measure_info_temp.json`
3. **Update existing `measure_info.json` files**: 
    - Search for ```*.csv.xz``` in the same directory, and check for a string match of the measure and the file name. If there is a match, appends the new elements into the ```measure_info.json```
    - Checks the `measure_info_template.json`, if there are elements that do not have required keys, appends those keys with values equal to `''`. Actual measures that need to be modified will be shown in the downstream tests
4. **Creates a ```manifest.json```**: 
    - Creates or overrides a ```manifest.json``` at the root directory with the: hash, file size (bytes), and file path of each file by looping through all folders that match ```**/distribution/``` 
