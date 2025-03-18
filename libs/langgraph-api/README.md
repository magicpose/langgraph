# graph-platform

配置环境变量 临时
# pg库
POSTGRES_URL=postgresql://postgres:postgres@10.1.3.122:5433/graph;
REDIS_URL=fake;

# bass
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyAgCiAgICAicm9sZSI6ICJhbm9uIiwKICAgICJpc3MiOiAic3VwYWJhc2UtZGVtbyIsCiAgICAiaWF0IjogMTY0MTc2OTIwMCwKICAgICJleHAiOiAxNzk5NTM1NjAwCn0.dc_X5iR_VP_qT0zsiyj_I_OZ2T9FtRU2BBNWN8Bu4GE;
SUPABASE_URL=http://10.1.3.122:8000;

# pub sub
KAFKA_SERVERS=10.1.3.122:9092;

# 可观测配置
LANGFUSE_HOST=http://10.1.3.122:3005;
LANGFUSE_PUBLIC_KEY=pk-lf-2f7f19a3-0cd2-47f2-bb5e-7bcf84a64ac6;
LANGFUSE_SECRET_KEY=sk-lf-e66fb8a1-d69f-4e34-8455-c27ae57cf4d9;

# cli 本地启动
1 service 本地测试启动
  langgraph_api.service
2 (推荐) cli.run_server main()
通过--config=你的配置文件(默认langgraph.json)， 启动langgraph-serve

# 后续
1 scp接口开发
2 提供不同粒度的接口规范
3 通过cli控制智能体容器
4 智能体容器动态回收*
*
<<
LANGGRAPH_AUTH_TYPE=langsmith;LANGGRAPH_CLOUD_LICENSE_KEY=12123123123;LANGSMITH_TENANT_ID=1;PYTHONUNBUFFERED=1;AGENT_AUTH_ENDPOINT=http://abc.com

REDIS_URL: redis://langgraph-redis:6379
DATABASE_URL: postgres://postgres:postgres@langgraph-postgres:5432/postgres?sslmode=disable
N_JOBS_PER_WORKER: "2"
LANGGRAPH_CLOUD_LICENSE_KEY: ${LANGGRAPH_CLOUD_LICENSE_KEY}
FF_JS_ZEROMQ_ENABLED: ${FF_JS_ZEROMQ_ENABLED}

* 
KAFKA_SERVERS=10.1.3.122:9092;LANGFUSE_HOST=http://10.1.3.122:3005;LANGFUSE_PUBLIC_KEY=pk-lf-2f7f19a3-0cd2-47f2-bb5e-7bcf84a64ac6;LANGFUSE_SECRET_KEY=sk-lf-e66fb8a1-d69f-4e34-8455-c27ae57cf4d9;POSTGRES_URL=postgresql://postgres:postgres@10.1.3.122:5433/graph;SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyAgCiAgICAicm9sZSI6ICJhbm9uIiwKICAgICJpc3MiOiAic3VwYWJhc2UtZGVtbyIsCiAgICAiaWF0IjogMTY0MTc2OTIwMCwKICAgICJleHAiOiAxNzk5NTM1NjAwCn0.dc_X5iR_VP_qT0zsiyj_I_OZ2T9FtRU2BBNWN8Bu4GE;SUPABASE_URL=http://10.1.3.122:8000;PYTHONUNBUFFERED=1

docker build -t  harbor.e-tudou.com/bpc-reference/langgraph-api:3.11   .

docker push  harbor.e-tudou.com/bpc-reference/langgraph-api:3.11 

LANGSERVE_GRAPHS
