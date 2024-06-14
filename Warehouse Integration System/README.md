# ELT Integration Project

## Project Overview
This project demonstrates an ELT (Extract, Load, Transform) process using SQL Server Integration Services (SSIS). The process extracts data from various sources, loads it into a staging area, and transforms it into a format suitable for reporting and analysis.

## Repository Contents
- **Warehouse11.sln**: Solution file for the SSIS project.
- **dtsx metadata.txt**: Metadata and configuration details for the SSIS packages used in this project.

## ELT Process Details
The ELT process consists of multiple SSIS packages, each performing specific tasks to extract, load, and transform the data. Below are the key components:

### Extract
The extraction process involves retrieving data from various sources using OLE DB connections.

![Data Flow](images/DataFlow.png)

- **OLE DB Source**: Configured to extract data from the AdventureWorksDW2019 database.
  - **Properties**:
    - `CommandTimeout`: Number of seconds before a command times out (0 for infinite).
    - `SqlCommand`: The SQL command to execute.

### Load
The loading process involves moving the extracted data into destination tables in a staging area.

![OLE DB Destination](images/OleDbDestination.png)

- **Data Flow Task 1**: Loads data into destination tables.
  - **OLE DB Destination**: Configured to load data into the AW_Germany database.
  - **Properties**:
    - `FastLoadOptions`: Options used with fast load.
    - `FastLoadMaxInsertCommitSize`: Specifies commit size during data insertion.

### Transform
The transformation process involves converting the loaded data into a format suitable for analysis.

![Transform Flow](images/TransformFlow.png)

- **Data Flow Task 2**: Transforms the loaded data.
  - **OLE DB Destination**: Configured for transformation processes.
  - **Properties**:
    - `SqlCommandVariable`: Variable containing the SQL command to execute.

## SSIS Package Configuration
The following images provide insights into the SSIS package configuration and tools used:

![SSIS Toolbox](images/ToolBox.png)

### Example of a Data Flow Task
![Data Flow Example](images/DataFlowExample.png)

### Creating Temporary Tables
Stored procedures used to create temporary tables for staging data:

![Temp Table Creation](images/TempCreation.png)

```sql
ALTER PROC [dbo].[CREATE_TEMP_TABLES]
AS
BEGIN
    IF NOT EXISTS (SELECT * FROM SYS.TABLES WHERE NAME=N'TEMP_DimAccount' AND type='U')
    BEGIN
        CREATE TABLE dbo.TEMP_DimAccount(
            [AccountKey] [int] NOT NULL,
            ...
        )
    END
    ...
END
