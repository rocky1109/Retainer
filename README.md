# Retainer
A RESTful WebService which helps to keep track of the state of objects.

## Installation
Clone this respository and install the requirements, as follows:
```python
>> git clone https://github.com/rocky1109/Retainer.git
>> pip install -r requirements.txt
```

## How to
### Run the WebServer
Start the web server, as follows:
```python
>> python app.py
```

### Change the settings
In the project directory there's **settings.json**, which has configuration parameters as follows:
* **SQL_DB_PATH**: (optional, str) Path where SQLite database will be created. <br />
                   Default path will be - *sqlite:///apps.sqlite3*
* **DEBUG**: (optional, bool) Starts the Flask WebServer in specified mode. <br />
                   Default will be - *false*
* **PORT**: (optional, int) Port on which Flask WebServer will be started. <br />
                   Default will be - *5000*
* **STATES**: (list) List of the states which will be retained sequentially and will be returned upon **GET** request. <br />
                   Example: *["NotStarted", "ProvisionBegin", "ProvisionDetected", "InstallBegin", "InstallCompleted", "ProvisionCompleted"]* <br />
                   For every object (upon **POST** request) it will automatically assign the first state from the list, <br />
                   and upon incrementing the state (from API) it will move the state to next state sequentially from the list.
* **NO_OF_STATES**: (int) Integer number, which assigns the no. of states for the object scope.
* **ERRORS**: (optional, list) List of errors. Objects can be updated to any of the error state specified in settings. <br />
                   Default will empty list, *[]*. <br />
                   Such that object will not be able to assign to any error state.


<br />

*NOTE*: Among the **STATES** and **NO_OF_STATES** either one needs to specified. Basically it, works in contrast. <br />
But when both fields are specified, then, **STATES** will be overtaken by **NO_OF_STATES** in **GET** requests.

### Use the APIs
To understand the APIs lets take configurations settings as follows:
```javascript
{
  "SQL_DB_PATH": "sqlite:///apps.sqlite3",
  "STATES": ["NotStarted", "ProvisionBegin", "ProvisionDetected", "InstallBegin", "InstallCompleted", "ProvisionCompleted"],
  "DEBUG": false,
  "PORT": 8080
}
```
* **POST** request: <br />
To create and save the object into database first you have to make the **post** request, which can be made as follows:
```
>> cURL -i -H "Content-Type: application/json" -X POST -d '{"name":"Office2k16"}' http://localhost:8080/api/v1.0/apps

{
  "app": {
    "created_at": "Thu, 01 Jun 2017 15:45:24 GMT",
    "name": "Office2k16",
    "state": "NotStarted",
    "updated_at": null,
    "error": null,
    "error_log": "",
    "uri": "http://127.0.0.1:8080/api/v1.0/apps/1"
  }
}
```
**NOTE**: Keep mind to add *content-type*=**application/json** in every request made to web server.

* **GET** request: <br />
To fetch the state for all the objects one will have to use **get** request, which can be made as follows:
```
>> cURL -i http://localhost:8080/api/v1.0/apps

{
  "apps": [
    {
      "created_at": "Thu, 01 Jun 2017 15:45:24 GMT",
      "name": "Office2k16",
      "state": "NotStarted",
      "updated_at": null,
      "error": null,
      "error_log": "",
      "uri": "http://127.0.0.1:8080/api/v1.0/apps/1"
    },
    {
      "created_at": "Thu, 01 Jun 2017 15:52:29 GMT",
      "name": "TeamViewer",
      "state": "NotStarted",
      "updated_at": null,
      "error": null,
      "error_log": "",
      "uri": "http://127.0.0.1:8080/api/v1.0/apps/2"
    },
    {
      "created_at": "Thu, 01 Jun 2017 15:52:50 GMT",
      "name": "Visio2k13",
      "state": "NotStarted",
      "updated_at": null,
      "error": null,
      "error_log": "",
      "uri": "http://127.0.0.1:8080/api/v1.0/apps/3"
    }
  ]
}
```
**NOTE**: When post request is made the object is saved with first *state* specified in configuration.

* **INCR** request: <br />
This is the **get** request which is made to *uri* of the returned object, which actually increments the state of object to the next state specified in list.
```
>> cURL -i http://localhost:8080/api/v1.0/apps/1/incr

{
  "app": {
    "created_at": "Thu, 01 Jun 2017 15:45:24 GMT",
    "name": "Office2k16",
    "state": "ProvisionBegin",
    "updated_at": "Thu, 01 Jun 2017 16:00:31 GMT",
    "error": null,
    "error_log": "",
    "uri": "http://127.0.0.1:8080/api/v1.0/apps/1"
  }
}
```
**NOTE**: When the object has completed being on all the states in sequence, there after when *incr* request is made then, server responds back with 404.
```
{
  "reason": "Reached to maximum state value.",
  "result": false
}
```

* GET **NAME** request: <br />
This is a **get** request, which gets the object(s) associated with name value of the object.
```
>> cURL -i http://localhost:8080/api/v1.0/apps/TeamViewer

{
  "apps": [
    {
      "created_at": "Thu, 01 Jun 2017 15:52:29 GMT",
      "name": "TeamViewer",
      "state": "NotStarted",
      "updated_at": null,
      "error": null,
      "error_log": "",
      "uri": "http://localhost:8080/api/v1.0/apps/2"
    }
  ]
}
```

* GET **ID** request: <br />
This is a **get** request, which gets the object associated with id value of the object.
```
>> cURL -i http://localhost:8080/api/v1.0/apps/3

{
  "app": {
    "created_at": "Thu, 01 Jun 2017 15:52:50 GMT",
    "name": "Visio2k13",
    "state": "NotStarted",
    "updated_at": null,
    "error": null,
    "error_log": "",
    "uri": "http://localhost:8080/api/v1.0/apps/3"
  }
}
```

* POST **ERROR** request: <br />
This is **post** request, which changes the state of object to specified error state and the actual **state** parameter is changed to null.
Takes to parameters: *error* (An error from list of **ERRORS**), and optional *error_log* (string specifying any error details)
```
>> cURL -i -H "Content-Type: application/json" -X POST -d '{"error":"ProvisionFailed", "error_log":"Disk was full"}' http://localhost:8080/api/v1.0/apps/1/error

{
  "app": {
    "created_at": "Thu, 01 Jun 2017 15:45:24 GMT",
    "name": "Office2k16",
    "state": null,
    "updated_at": "Thu, 01 Jun 2017 16:00:31 GMT",
    "error": "ProvisionFailed",
    "error_log": "Disk was full",
    "uri": "http://127.0.0.1:8080/api/v1.0/apps/1"
  }
}
```
**NOTE**: Subsequently any calls (apart from **GET** & **DELETE** request) made to this object, will not be allowed made.

<br /> <br />
Similary, **PUT** and **DELETE** requests are made over the WebService.

