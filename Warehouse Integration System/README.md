# ELT Integration Project

## Project Overview
This project demonstrates an ELT (Extract, Load, Transform) process using SQL Server Integration Services (SSIS). The process extracts data from various sources, loads it into a staging area, and transforms it into a format suitable for reporting and analysis.

## Repository Contents
- **Warehouse11.sln**: Solution file for the SSIS project.
- **dtsx metadata.txt**: Metadata and configuration details for the SSIS packages used in this project.

## Data Warehouse Purpose
The data warehouse serves as a central repository for storing and organizing data from multiple sources. It is designed to support reporting, analysis, and decision-making processes for business users and stakeholders.

### Dimensional Model
The dimensional model is a data modeling technique used in data warehousing. It organizes data into dimensions (e.g., Date, Customer, Product) and fact tables (e.g., Survey_Response, FactCurrencyRate). Dimensions provide descriptive attributes for analysis, while fact tables store the measurable metrics.

### ELT Process
The Extract, Load, Transform (ELT) process is used to populate the data warehouse.
- **Extraction**: Involves extracting data from the AdventureWorks database and flat files.
- **Loading**: Involves loading the extracted data directly into the data warehouse without immediate transformation.
- **Transformation**: Takes place within the data warehouse using its processing capabilities to cleanse, filter, and aggregate the data to meet business requirements.

During the ELT process, SQL Server Management Studio (SSMS) is used to design the database schema, procedures, views, and other components.

## Parallel Processing in SSIS
### Multiple Threads
In SSIS, you can configure the package to use multiple threads to execute tasks in parallel. By dividing the workload among multiple threads, each working on a separate task, you can leverage the processing power of your system's CPU and reduce overall execution time. SSIS provides options to control the degree of parallelism, allowing you to specify the number of threads to use.

### Parallel Data Flow Tasks
SSIS allows you to split your data flow into multiple paths and execute them in parallel. For example, if you have multiple fact tables to load, you can create separate data flow tasks for each table and execute them simultaneously. This approach utilizes the available system resources effectively and can significantly speed up the data loading process.

### Benefits of Parallel Processing
- **Improved Performance**: By executing tasks in parallel, you can leverage the processing power of your system and reduce the overall execution time of your SSIS package.
- **Resource Utilization**: Parallel processing enables efficient utilization of system resources like CPU and memory, maximizing their potential.
- **Scalability**: Parallel processing allows for scalability as you can increase the number of threads or data flow paths to handle larger datasets or increased workloads.

## SSIS Package Structure
The SSIS package automates the ELT process, consisting of control flow tasks and data flow tasks that orchestrate the extraction, loading, and transformation of data.

### Control Flow
The control flow manages the execution and sequencing of tasks, ensuring that the ELT process follows the desired sequence and dependencies.

![Control Flow](images/ControlFlow.png)

### Data Flow
The data flow tasks handle the movement and transformation of data from source to destination.

![Data Flow](images/DataFlow.png)

### Staging Area
The staging area is an intermediate storage area where data is temporarily stored during the ELT process. It helps in data validation, cleansing, and applying necessary transformations before loading the data into its final tables.

### Dimension and Fact Tables
- **Dimension Tables**: Contain descriptive attributes and hierarchies for analysis (e.g., DimDate, DimCustomer).
- **Fact Tables**: Store the measurable metrics and facts associated with the business processes (e.g., FactCurrencyRate, FactCallCenter).

### Temporary Tables and Views
Temporary tables are created to stage and store data during the ELT process. Views are created to consolidate data from multiple databases or sources.

![Temporary Tables and Views](images/TempTablesViews.png)

### Stored Procedures
Stored procedures encapsulate and execute specific logic or calculations on the data. They enhance the functionality and flexibility of the data warehouse for reporting and analysis purposes.

![Stored Procedures List](images/ProcedureList.png)

## Example of SSIS Package Execution
### Sequence of Tasks
1. **SQL Task (Create Temp Tables)**: Outside the For Each Loop container.
2. **Truncate Temp Tables**: Inside the For Each Loop container.
3. **Transfer Data to Temp Tables**: Inside the For Each Loop container.
4. **Exchange Temp Tables with Original Tables**: Inside the For Each Loop container.
5. **SQL Task (Add Constraints to Temp Tables)**: Inside the For Each Loop container.
6. **SQL Task (Cleaning Null Values)**: Inside the For Each Loop container.
7. **Database Integrity Check**: After the For Each Loop container.

### Detailed View of Data Flow Tasks
![ELT (AdventureWorks to DBCenter) Dimensional tables](images/ELT-Dimensional.png)
![ELT (AdventureWorks to AW_Italy DB) Fact tables](images/ELT-Fact.png)

## Sales Trend Analysis Examples
### Monthly Sales Trend
```sql
SELECT
    DATEPART(MONTH, OrderDate) AS SalesMonth,
    SUM(ListPrice) AS TotalSalesAmount
FROM
    AW_Italy.dbo.FactInternetSales
WHERE
    SalesTerritoryGroup = 'Europe'
GROUP BY
    DATEPART(MONTH, OrderDate)
ORDER BY
    DATEPART(MONTH, OrderDate);
