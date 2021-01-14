# TODO
1. tests for review module (scott)
1. add ability to save/load backup of data (new module: backup.py)
1. add ability to change data storage location
1. Automatic periodic backup of data
1. Improve error/exception handling in utils.safe_commit()
1. Implement option to launch editor for interactive categorization (see [click.edit()](https://click.palletsprojects.com/en/7.x/utils/#launching-editors))
1. Implement option to pause categorization partway through, then resume later (example, pause to add new category)
1. Add module to set "category suggestions" from CLI (ie, user can set keywords which, if matched in the transaction description, will move the starting point of the category selection pointer (ie, Pick module default))
1. look into abstracting management of user and categ (ie, both have add, update, delete, get) functions
1. add ability to set order of categories in pick menu 
1. add final review of all categorized transactions before committing to the db
1. add ability to filter by date
1. make 'print_output' function for standardizing formatting to cli ouput
1. Make categories user-specific