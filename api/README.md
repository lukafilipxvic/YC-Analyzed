# YC Vault API

## Overview

The YC Vault API is a RESTful API that provides access to the YC Combinator startup data.

## Endpoints

### Root Endpoint

```
GET /
```

Returns basic API information.

**Response**: `200 OK` with API information

### Get Companies

```
GET /v1/companies
```

Get YC companies with filtering options. This endpoint returns YC companies from the dataset closest to the provided date. You can filter companies by batch, status, industry, city, and team size.

**Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| date | string | Date in YYYY-MM-DD format |
| batch | string | YC batch (e.g., W21, S22) |
| status | string | Company status (Active, Acquired, Inactive, Public) |
| industry | string | Industry category |
| city | string | Company's city location |
| team_size | integer | Team size |
| limit | integer | Limit the number of records returned |
| offset | integer | Offset for pagination (default: 0) |

**Response**: `200 OK` with company data

### Get Founders

```
GET /v1/founders
```

Get YC founders with filtering options. This endpoint returns YC founders from the dataset closest to the provided date. You can filter founders by their company's batch, status, industry, city, and founder's name.

**Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| date | string | Date in YYYY-MM-DD format |
| batch | string | YC batch (e.g., W21, S22) |
| status | string | Company status (Active, Acquired, Inactive, Public) |
| industry | string | Industry category |
| city | string | Company's city location |
| first_name | string | Founder's first name |
| last_name | string | Founder's last name |
| limit | integer | Limit the number of records returned |
| offset | integer | Offset for pagination (default: 0) |

**Response**: `200 OK` with founder data

### Dataset Endpoints

#### List Datasets

```
GET /v1/datasets/datasets
```

List all available dataset dates.

**Response**: `200 OK` with array of available dataset dates

#### Get Dataset Files

```
GET /v1/datasets/datasets/{dataset_date}
```

Get available files for a specific dataset date.

**Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| dataset_date | string | Date of the dataset (path parameter) |

**Response**: `200 OK` with available files information

#### Get Dataset Data

```
GET /v1/datasets/datasets/{dataset_date}/{file_name}
```

Get data from a specific file in a dataset.

**Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| dataset_date | string | Date of the dataset (path parameter) |
| file_name | string | Name of the file (path parameter) |
| limit | integer | Limit the number of records returned |
| offset | integer | Offset for pagination (default: 0) |

**Response**: `200 OK` with file data

## Error Handling

The API returns standard HTTP status codes to indicate the success or failure of an API request.

| Status Code | Description |
|-------------|-------------|
| 200 | OK - The request was successful |
| 422 | Validation Error - The request parameters failed validation |

For validation errors, the response will include details about which parameters failed validation and why.

## Examples

### Get companies from Winter 2021 batch

```
GET /v1/companies?batch=W21
```

### Get active founders in San Francisco

```
GET /v1/founders?status=Active&city=San%20Francisco
```

### Get list of available datasets

```
GET /v1/datasets/datasets
```

### Get company data from a specific dataset

```
GET /v1/datasets/datasets/2023-01-01/companies.json
```


