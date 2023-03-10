# WTOP
Wtop is a lightweight web-based system monitor made with Python and aiohttp.
![изображение](https://user-images.githubusercontent.com/83316072/222916009-a57a2f9c-fc07-4e10-a420-23f69346f02d.png)

## endpoints

### Json endpoint
```
/stats.json
```
sample output:
```
{
  "cpu": {
    "cpu_count": 2,
    "thread_count": 4,
    "utilization": {
      "overall": 8.3,
      "per_cpu": [
        4.5,
        0,
        9.2,
        1.5
      ]
    }
  },
  "memory": {
    "total": 17024741376,
    "available": 8209461248,
    "percent": 51.8,
    "used": 8815280128,
    "free": 8209461248
  }
}
```

### HTML endpoint

```
/ or /stats.html
```
The data on the page is updated in real time via a websocket.
![изображение](https://user-images.githubusercontent.com/83316072/222916024-f6d8c4ae-73ce-4821-999f-eb07a04a099e.png)


### Websocket endpoint

```
/stats.ws
```
When receiving a connection, wtop sends data in the json format shown above every second



## Installation

### via poetry

```
>> git clone https://github.com/1ort/wtop.git
>> cd wtop
>> poetry install
>> poetry run python -m wtop
```

## Todo

- Unit-tests
- View active processes
- User authentication
- Disk info


