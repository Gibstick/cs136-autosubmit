cs136-autosubmit
================

Automatically submit assignments to Marmoset. It scans your assignments for a special line containing the class and assignment info, and passes it along to https://github.com/hkpeprah/marmoset. 

What works
----------
Submit all .rkt files in the current directory that contain this line:

`;;;!(autosubmit class assignment)`

For example, `;;;(autosubmit cs136 a1p0e)`

And all .c files that have

`///autosubmit class assignment`

Todo
----
- ~~submit multiple files for one assignment~~
- ~~support for .c files~~
- support for arbitrary file types with an "autosubmit-rules" file

License
-------
See LICENSE
