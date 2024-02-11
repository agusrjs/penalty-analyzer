# Penalty analyzer script

This project aims to determine effectiveness parameters for penalty kicks in football. The goal is to create an efficient method for assessment and monitoring. To achieve this, it relies on the recording and observation of the execution.

The script, named `penalties.py`, calculates specific parameters related to soccer penalty kicks. The script processes data exported from Nacsport in format 2 and relies on values from a `Parameters.xlsx` file provided by the user.

## Prerequisites

Before running the script, ensure the existence of the `Parameters.xlsx` file, containing the necessary parameters such as frames per second (fps), image dimensions, goal dimensions, penalty distance, and error values.

If the `Parameters.xlsx` file is not found, the script will create a template for it and prompt the user to fill in the required values before execution.

## Parameters

The parameters calculated by the script include:
- Average launch speed
- Ball distance to the center of the goal when crossing the goal line

## Input

The script takes as input an Excel file exported by Nacsport in format 2. The file should contain data derived from a template with the following specifications:
- Category: Player taking the penalty kick
- Descriptors:
  - Execution date (assigned automatically to each category)
  - Quadrant of the penalty goal (1 to 4, starting from the top-right and moving counterclockwise)
  - Result (goal, post, miss)
  - Graph: XY pair indicating the ball's destination upon reaching the goal line

## Output

The script produces a CSV file named `penalties***.csv` in the same directory, where `***` represents the processed file number. Additionally, it appends the calculated records to `penalties.csv`, a file that accumulates all records.

## Usage

Run the script and follow the prompts to select the Nacsport-exported file. The script will then process the data, perform calculations, and export the results. A final dialog box will confirm the completion of the execution. The 'dataframes' folder contains two .xlsx files of penalty kicks that can be loaded.

## Dependencies

- pandas
- numpy
- tkinter (for file dialog)
- messagebox (from tkinter)

## Author

- Agustín Germán Rojas
- Email: agustingermanrojas@gmail.com

## License

This script is open-source and free to use. Feel free to contribute and enhance its functionality.
