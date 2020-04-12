README

Sources

1) Johns Hopkins Data
2) Worldometer (Scraping for population and testing)
3) https://ourworldindata.org/covid-testing
4) World Bank Data


Variables:

1) country
3) total population
2) total infections per capita
3) max infections in single day per capita
4) government effectiveness measure (between -2.5 and 2.5)
5) median age
6) total tests per capita
7) law_enforcement_ability
8) corruption level
9) human freedom
10) stringency index

Instructions:

Script will automatically remove data that is not complete. In order to add data you must change the required values to reflect
the new variable (right now it is 6 you should change it to however many total variables present). Make sure you compare your scraping/new dataset
country names to country names in the database and add that to aliases (US = USA = United States). A data value should not be deleted
just because it has a variation of a name. Uncomment out the print statements in cleaning portion to see which values were deleted and which ones you should
double check. To put figures out there, original db had 181 countries however after cleaning only 110 are remaining. 

Data: 

data is stored in infections.json.