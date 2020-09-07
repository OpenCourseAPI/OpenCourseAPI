# OpenCourseAPI

An open-source API to scrape, process, and serve college course and class data 📒

(Also, a fresh take on [OwlAPI](https://github.com/OpenCourseAPI/OwlAPI) =D)

## Features

- 🔍&nbsp; Scrapes **terms, deptartments, courses, and classes**
- 🧩&nbsp; **Campus-agnostic architecture** allows easy extensibility
- 📅&nbsp; Currently serves **10+ years** of just FHDA data
- 🏫&nbsp; Scrapes a total of **4 colleges** (adding more is just a matter of time)

**Coming Soon:**

- 📙 Scrape **course catalogs** to get more course info, such as descriptions
- 🔗 **Link classes to professors** for advanced analytics
- 🌐 **GraphQL API** (proof-of-concept finished)


## **Data Explorer => [opencourse.dev](https://opencourse.dev)**

_URL is subject to change.. but for now, the frontend and the API are hosted on the same domain._


## API Docs

Currently, the following data for the following campuses exists:

| id | name |
| --- | --- |
| `fh` | Foothill College |
| `da` | De Anza College |
| `wv` | West Valley College |
| `mc` | Mission College |

All endpoints (except for `/:campus`) support the following query parameters:

| name | format | default |
| ---- | ------ | --- |
| `year` | a valid year | 2020 |
| `quarter` | `fall`, `winter`, `spring`, or `summer` | fall |

Example: [/da/depts?year=2019&quarter=fall](https://opencourse.dev/da/depts?year=2019&quarter=fall)

#### `/:campus`

Example: [/fh](https://opencourse.dev/fh)

Get **campus metadata information**.

<details>
<summary>
Sample Response
</summary>

```json
{
  "id": "fh",
  "terms": [
    {
      "year": 2020,
      "term": "summer",
      "code": "202111"
    },
    {
      "year": 2020,
      "term": "spring",
      "code": "202041"
    },
    {
      "year": 2020,
      "term": "winter",
      "code": "202031"
    },
    {
      "year": 2019,
      "term": "fall",
      "code": "202021"
    },
    {
      "year": 2020,
      "term": "fall",
      "code": "202121"
    }
  ]
}
```

</details>


#### `/:campus/courses`

Example: [/fh/courses](https://opencourse.dev/fh/courses)

Get **all courses** at a campus for the selected term and year.

<details>
<summary>
Sample Response
</summary>

```json
[
  {
    "dept": "ACTG",
    "course": "1A",
    "title": "Financial Accounting I"
  },
  {
    "dept": "ACTG",
    "course": "1B",
    "title": "Financial Accounting II"
  },
  {
    "dept": "MATH",
    "course": "1A",
    "title": "Calculus"
  }
]
```

</details>


#### `/:campus/classes`

Example: [/fh/classes](https://opencourse.dev/fh/classes)

Get **all classes** at a campus for the selected term and year.

<details>
<summary>
Sample Response
</summary>

```json
[
  {
    "CRN": 20238,
    "raw_course": "ACTG F001A01W",
    "dept": "ACTG",
    "course": "1A",
    "section": "01W",
    "title": "Financial Accounting I",
    "units": 5,
    "start": "10/19/2020",
    "end": "12/11/2020",
    "seats": 2,
    "wait_seats": 15,
    "status": "open",
    "times": [
      {
        "days": "TBA",
        "start_time": "TBA",
        "end_time": "TBA",
        "instructor": [
          "Joe L  Mayer (P)"
        ],
        "location": "FC ONLINE"
      }
    ]
  },
  { "...": "..." }
]
```

</details>


#### `/:campus/classes/:crn`

Example: [/fh/classes/20238](https://opencourse.dev/fh/classes/20238)

Get a **class by its `CRN`** (in a given term and year).

<details>
<summary>
Sample Response
</summary>

```json
{
  "CRN": 20238,
  "raw_course": "ACTG F001A01W",
  "dept": "ACTG",
  "course": "1A",
  "section": "01W",
  "title": "Financial Accounting I",
  "units": 5,
  "start": "10/19/2020",
  "end": "12/11/2020",
  "seats": 2,
  "wait_seats": 15,
  "status": "open",
  "times": [
    {
      "days": "TBA",
      "start_time": "TBA",
      "end_time": "TBA",
      "instructor": [
        "Joe L  Mayer (P)"
      ],
      "location": "FC ONLINE"
    }
  ]
}
```

</details>


#### `/:campus/depts`

Example: [/fh/depts](https://opencourse.dev/fh/depts)

Get **all departments** at a campus for the selected term and year.

<details>
<summary>
Sample Response
</summary>

```json
[
  {
    "id": "GIST",
    "name": "Geospatial Tech & Data Sci"
  },
  {
    "id": "GLST",
    "name": "Global Studies"
  },
  {
    "id": "GID",
    "name": "Graphic and Interact Desig"
  }
]
```

</details>


#### `/:campus/depts/:dept`

Example: [/fh/depts/GLST](https://opencourse.dev/fh/depts/GLST)

Get **a department** at a campus for the selected term and year.

<details>
<summary>
Sample Response
</summary>

```json
{
  "id": "GLST",
  "name": "Global Studies"
}
```

</details>


#### `/:campus/depts/:dept/classes`

Example: [/fh/depts/MATH/classes](https://opencourse.dev/fh/depts/MATH/classes)

Get **all classes in a department** for the selected term and year.

<details>
<summary>
Sample Response
</summary>

```json
[
  {
    "CRN": 20086,
    "raw_course": "MATH F001A01V",
    "dept": "MATH",
    "course": "1A",
    "section": "01V",
    "title": "Calculus",
    "units": 5,
    "start": "09/21/2020",
    "end": "12/11/2020",
    "seats": 0,
    "wait_seats": 7,
    "status": "waitlist",
    "times": [
      {
        "days": "MW",
        "start_time": "07:30 AM",
        "end_time": "09:45 AM",
        "instructor": [
          "Diana Monica  Uilecan (P)"
        ],
        "location": "FH ONLINE"
      }
    ]
  },
  { "...": "..." }
]
```

</details>


#### `/:campus/depts/:dept/courses`

Example: [/fh/depts/MATH/courses](https://opencourse.dev/fh/depts/MATH/courses)

Get **all courses in a department** for the selected term and year.

<details>
<summary>
Sample Response
</summary>

```json
[
  {
    "dept": "MATH",
    "course": "1A",
    "title": "Calculus",
    "classes": [
      20086,
      20087,
      20088,
      20257,
      20761,
      20762,
      20305,
      21310
    ]
  },
  {
    "dept": "MATH",
    "course": "1B",
    "title": "Calculus",
    "classes": [
      20672,
      20089,
      20769,
      20773
    ]
  }
]
```

</details>


#### `/:campus/depts/:dept/courses/:course`

Example: [/fh/depts/MATH/courses/1A](https://opencourse.dev/fh/depts/MATH/courses/1A)

Get **a course in a department** for the selected term and year.

<details>
<summary>
Sample Response
</summary>

```json
{
  "dept": "MATH",
  "course": "1A",
  "title": "Calculus",
  "classes": [
    20086,
    20087,
    20088,
    20257,
    20761,
    20762,
    20305,
    21310
  ]
}
```

</details>


#### `/:campus/depts/:dept/courses/:course/classes`

Example: [/fh/depts/MATH/courses/1A/classes](https://opencourse.dev/fh/depts/MATH/courses/1A/classes)

Get **all classes for a course** in the selected term and year.

<details>
<summary>
Sample Response
</summary>

```json
[
  {
    "CRN": 20086,
    "raw_course": "MATH F001A01V",
    "dept": "MATH",
    "course": "1A",
    "section": "01V",
    "title": "Calculus",
    "units": 5,
    "start": "09/21/2020",
    "end": "12/11/2020",
    "seats": 0,
    "wait_seats": 7,
    "status": "waitlist",
    "times": [
      {
        "days": "MW",
        "start_time": "07:30 AM",
        "end_time": "09:45 AM",
        "instructor": [
          "Diana Monica  Uilecan (P)"
        ],
        "location": "FH ONLINE"
      }
    ]
  },
  { "...": "..." }
]
```

</details>


## Examples

### Python

Install `requests`, and use the API as follows:

```python
import requests

API_URL = 'https://opencourse.dev'
req = requests.get(f'{API_URL}/fh/courses')

if req.ok:
    courses = req.json()

    for course in courses:
        print(course['dept'], course['course'], course['title'])
```

<details>
<summary>View Output</summary>

```
ACTG 1A Financial Accounting I
ACTG 1B Financial Accounting II
ACTG 1C Managerial Accounting
ACTG 51A Intermediate Accounting I
ACTG 52 Advanced Accounting
ACTG 53 Financial Statement Analysis
ACTG 54 Accounting Information Systems
ACTG 58 Auditing
ACTG 59 Fraud Examination
ACTG 60 Accounting for Small Business
ACTG 64A Computerized Accounting Practice Using Quickbooks
ACTG 64B Computerized Accounting Practice Using Excel
ACTG 65 Payroll & Business Tax Accounting
ACTG 66 Cost Accounting
ACTG 67 Tax Accounting
...
```

</details>


## Development

For running the API server, install `python` 3.8, `pip`, and `pipenv`.

Note: the following is subject to change (especially the scraper modules)

```bash
git clone https://github.com/OpenCourseAPI/OpenCourseAPI.git
cd OpenCourseAPI

pipenv install # install all python dependencies

python -m campus.fhda.fhda_scrape # scrape Foothill / De Anza College
pythom -m campus.wvm.wvm_scrape # scrape West Valley / Mission College

python server.py # start the server
```

To run the frontend, install `Node.js` (preferably v12+) and `yarn`. Afterwards, run the following:

```bash
cd frontend
yarn install # install NPM packages
yarn start # start dev server
```

To build for production, use:

```bash
yarn run build
```

The generated static files are in `frontend/build`.


## Contribute

All contributions are welcome! A contribution guide is TBA.. but you can start by [opening an issue](https://github.com/OpenCourseAPI/OpenCourseAPI/issues/new) and looking at the development guide above. Thanks!

### Core Team

- [**Madhav Varshney**](https://github.com/madhavarshney)
- [**Kishan Emens**](https://github.com/phi-line)


## License

[MIT License](LICENSE)
