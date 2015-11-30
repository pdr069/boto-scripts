# boto-scripts
DynamoDB boto scripts for use in replicating things like indexes,
table schema dumping, table creation, etc.

* create_missing_indexes.py:

This script takes a master table name and a replica table name and
will ensure that the global_secondary_indexes are added to a replica
table.  

This is helpful for those people that are using cross-region
replication with DynamoDB in the case of making a replica a master
table.  Replication seems to omit the indexes upon duplication
which I'm not sure is a side-effect of how I setup replication by
not boot-strapping the table or if it's just normal for tables to be
replicated in this way.

* add_acl.py

This script just adds network acls as needed.  Use --help for full usage.
