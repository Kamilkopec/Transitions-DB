# Transitions-DB
All automation related to transiton db - auditing, small checks, api in the future.


1. TransitionsAudit - code created to manage caret returns and ',' in product description name.
 a. it takes as an input an csv extract from an company's database,
 b. iterates with pandas through each row and column searching for ',', '\n', '\r' and removes them.
 c. the final corrected field are saved in files containing column names and recodr id
 d. after that we are importing them via database gui tools (future selenium or api?)
 
