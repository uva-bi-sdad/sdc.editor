# sdc.editor

This repo provides automated edits for miscellaneous tasks maintaining data repositories. The editor is expected to perform edits in the following sequence:

1. **Auto generate directory structures**:
    - If ```**/distribution``` is found, the editor additionally creates `code`, `data`, and `docs` folders underneath them for any one missing
2. **Create a placeholder `measure_info.json` files**: 
    - Loop through each `**/distribution/`. If a `*.csv.xz` is found, but a `measure_info.json` was not found in the same directory, create an empty placeholder `measure_info.json`
3. **Update existing `measure_info.json` files**: 
    - Search for ```*.csv.xz``` in the same directory, and check for a string match of the measure and the file name. If there is a match, appends the new elements into the ```measure_info.json```
    - Checks the `measure_info_template.json`, if there are elements that do not have required keys, appends those keys with values equal to `''`. Actual measures that need to be modified will be shown in the downstream tests
4. **Creates a ```manifest.json```**: 
    - Creates or overrides a ```manifest.json``` at the root directory with the: hash, file size (bytes), and file path of each file by looping through all folders that match ```**/distribution/``` 
