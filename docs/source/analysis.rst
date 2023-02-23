==================
Lab Space Analysis
==================

Description

Analysis Workflow
#################

Specifying Variables
*******************

Aliasing Variables
------------------

Cross Referencing Variables
---------------------------

Indepdent Variables
-------------------

Dependent Variables
-------------------

Control Variables
-----------------

Processing Data
***************

Specifying Plots
****************

Filtering Data
**************

To filter data, you can use the ``filter`` variable in your configuration file.
Filter can have the following members:
- ``rm_unused_cols``: (bool) Remove columns that are not used by cross reference, independent,
  dependent, or control variables. (Currently only works when these variables are used without conditions, plans to extend this)
- ``include_vals`` and ``exclude_vals``: (dict) Include or exclude values from a column. The key is the column name, and the value is a list of values to include or exclude. If a value is in both lists, it will be excluded. The keys specify columns, while values should be represented as a list over which to select elements. If the list is empty, all elements will be included/excluded. If the value is None, this column will be ignored.
- ``include_cols`` and ``exclude_cols``: (list) Include or exclude columns. If a column is in both lists, it will be excluded. If the list is empty, all columns will be included/excluded. If the value is None, all columns will be ignored.

Values passed into the filter can either be discrete or a range. To get a range, specify and internal list with the lower and upper values. For an inequality, specify a list with either the first or second element as "" to get minimum and maximum values, respectively. If you want this to be exclusive, you can add a third element as false.


Analysis CLI
############


Installing the CLI
******************