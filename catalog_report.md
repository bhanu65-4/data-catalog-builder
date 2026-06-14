# Data Catalog Report
## customers (csv)
**Path:** data\customers.csv
| Column | Type | Description | Sample values |
|---|---:|---|---|
| customer_id | int64 | Unique customer identifier. | 1, 2, 3 |
| first_name | object | Customer's first name. | Alice, Bob, Carol |
| last_name | object | Customer's last name. | Smith, Jones, Lee |
| email | object | Customer email address used for communication. | alice@example.com, bob@example.com, carol@example.com |
| signup_date | object | Date when the customer registered. | 2022-01-05, 2022-03-12, 2022-07-22 |

## employees (csv)
**Path:** data\employees.csv
| Column | Type | Description | Sample values |
|---|---:|---|---|
| employee_id | int64 | Unique employee identifier. | 1, 2, 3, 4, 5 |
| name | object | Name of the name. | Employee 1, Employee 2, Employee 3, Employee 4, Employee 5 |
| age | int64 | Employee age in years. | 25, 26, 27, 28, 29 |
| salary | int64 | Employee compensation amount. | 36000, 37000, 38000, 39000, 40000 |

## orders (csv)
**Path:** data\orders.csv
| Column | Type | Description | Sample values |
|---|---:|---|---|
| order_id | int64 | Unique identifier for the order. | 1001, 1002, 1003 |
| customer_id | int64 | References the customer who placed the order. | 1, 2, 1 |
| amount | float64 | Total order amount. | 19.99, 5.49, 12.0 |
| order_date | object | Date when the order was placed. | 2022-02-01, 2022-02-05, 2022-03-10 |

