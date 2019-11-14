config_center
=====
- 基于`Redis PUB/SUB`功能，实现不需要发版可以实时更新配置文件。
- 使用Flask简单方便，也可以把逻辑封装在自己项目里，例如Django等等。
- 前端部分可以找前端同事写个简易vue，或在已有后台管理页面新增页面调用api接口。

code structure
=====
- client目录，客户端代码在不同机器上执行
- server目录，服务器代码，可以`python3 run.py`执行本地应用服务，或使用uwsgi+nginx，部署在服务器上
- test.py：一个简易单元测试
```
.
├── conf
│   ├── client
│   │   ├── api.py
│   │   ├── __init__.py
│   │   └── tests.py
│   ├── __init__.py
│   └── server
│       ├── conf.log
│       ├── decorators.py
│       ├── __init__.py
│       ├── models.py
│       ├── run.py
│       ├── settings.py
│       └── views.py
├── docs
│   ├── init.sql
│   └── uwsgi.ini
├── LICENSE
└── requirements.txt
```

system structure
=====
<div align=center><img width="50%" height="50%" src="https://raw.githubusercontent.com/rubinera1n/config_center/master/static/diagram.png"/></div>
