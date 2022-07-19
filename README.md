# Provision services via NSO/EPNM

Configuring services on routers using Cisco EPNM API and Cisco NSO (will be added in the future)

Features simple web page on Flask framework with search/sort functions, with the possibility to deploy or delete service on routers using EPNM API and pre-loaded to EPNM templates (written using Apache VTL). Templates can be found in [separate file](static/epnm_templates.txt)
Also, there's a separate module for SEP management (data stored in DB using SQLite).

### Dependencies:

```pip install requests flask flask_sqlalchemy pandas ```


### SEP
SEP is a customer-side backdoor link, which requires a service to be deployed as EVPN instances with BVI interfaces, simultaneously on two routers, rather than as a set of subinterfaces on one router

## launch using 
```python bs_app.py``` 

or

```
$ export FLASK_APP=bs_app
$ flask run
```
