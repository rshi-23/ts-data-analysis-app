# ts-data-analysis-script

## Change Log
### July 5, 2021
* Added LD Probe(Block Avg) button and functionality
* Added LD Probe(ID Avg) button and functionality
### July 4, 2021
* Added LD Probe(Last Day Avg) button and functionality
### July 3, 2021
* Added LD Train (Select Animal ID) button and functionality
* Added LD Probe (Last Day Difficulty All) button and functionality
* Added LD Probe (Select Day) button and functionality
* Added LD Probe (Select ID) button and functionality
* Added LD Probe (Select Block) button and functionality
### July 2, 2021
* Fixed the LD Train output csv
* All animals now stop at the criteria met day or the very last day of test if the criteria was not met
* Added an option to LD Train to select which day for all animals
* Added an option to LD Train to select all first day for all animals  
* Added an option to LD Train to select all last criteria met day for all animals
* Started working on the GUI
	* Added LD Train (All) button and functionality
	* Added LD Train (Select Day) button and functionality
	* Added LD Train (First Day) button and functionality
	* Added LD Train (Last Day) button and functionality

### July 1, 2021
* Fixed first and second reversal trial amounts
* Fixed first and second reversal percent correctness
* Fixed second reversal duration

### June 28, 2021
* Fixed first and second reversal trial amounts
	* Trials count towards the next reversal
* Fixed the first and second reversal session duration
	* Changed the time back into seconds
	* If the first reversal was not met, then it will be placed at 1800 seconds
	* Changed the second reversal session length into duration, instead of absolute time
* Fixed the first and second reversal percent correctness
* Fixed the duplication detection
	* Duplicates are now detected by sorting the dataframe by total trial amount and session runtime. The script will keep the animals that have a greater total trial amount and total session runtime.
* Added the ability to extract the last day of each difficulty for LD Probe
* Added the merged_file.csv and dropped_duplicates.csv
* Fixed a bug with macOS index out of range error
	* Caused by having a different file system than Windows


### June 24, 2021
* Added difficulty type for each animal
* Added percent correctness for the first and second reversal

### June 17, 2021
* Added Date for each animal
* Added ID for each animal
* Added SessionLength for each animal
* Added NumberOfTrials for each animal
* Added overall PercentCorrect for each animal
* Added NumberOfReversals for each animal
* Added TotalITITouches for each animal
* Added TotalBlankTouches for each animal
* Added MeanRewardCollectionLatency for each animal
* Added MeanCorrectTouchLatency for each animal
* Added SessionLengthTo1stReversal for each animal
* Added NumberOfTrialTo1stReversal for each animal


