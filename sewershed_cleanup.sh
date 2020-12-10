# Remove newlines in the address attributes.
# SQLite represents newline as `char(10)` (no escape sequences).
v.db.update map=sewersheds column=WAADDR query_column="REPLACE(WAADDR, char(10), ' ')"
