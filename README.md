# playground-evedata-aws-cdk

after watching [aws cdk intro](https://www.youtube.com/watch?v=ZWCvNFUN-sU) i was really interested in cdk...

this repo contains my first run with aws-cdk to create a simple infrastructure stack.

####  cdk stack will create:
- one ec2 instance to compute eve online market data (no-source) 
- mysql rds instance for static data (eve online sde)
- elasticsearch to store and present market orders and trade posibilities

### initialise the first and empty stack:
```
npm install -g aws-cdk
cdk --version
mkdir playground-evedata-aws-cdk
cd playground-evedata-aws-cdk/
cdk init
cdk init --language=python app
python3 -m venv .env
source .env/bin/activate
pip install -r requirements.txt
```

### deploy stack
```
cdk deploy
```


### files to look at:
- [setup.py](setup.py)
- [app.py](app.py)
- [playground_evedata_aws_cdk_stack.py](playground_evedata_aws_cdk/playground_evedata_aws_cdk_stack.py)


## planning and open todos:

ec2:
- public instance, ssh key is used
- internals ip from ec2 will be whitelisted on mysql and elasticsearch

mysql:
- rds mysql, very simple deployment, reachable only from ec2 only

elasticsearch:
- elasticsearchdomain with kibana
- reachable from ec2
- reachable from my current public ip
  - can i add parameters into cdk deploy to specify my ip?

notes:
- default vpc
- evedata source will not exposed in this repo


open todos:
- lookup data from:
  - existing aws services
    - vpcips = names, ids
    - ec2 instances = internal and external ip



example run of trade calculation:
```
[..]
url https://esi.evetech.net/v1/markets/10000002/orders/
x-pages: 314
len: 1236539
(1236539, [])

real	2m54.261s
user	1m2.416s
sys	0m3.274s


(.env) [root@ip-10-0-14-204 evedata]# time python3 trades_jita_buy.py
delete index
create index
(9304, [])
run over orders: 1236539
trades for db 9304
skip counter 1227235

real	8m22.153s
user	2m19.178s
sys	0m12.260s
 ```
