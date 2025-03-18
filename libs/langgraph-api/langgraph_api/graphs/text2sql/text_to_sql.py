from sqlalchemy import (
    Column,
    Float,
    Integer,
    MetaData,
    String,
    Table,
    create_engine,
    insert,
    inspect,
    text,
)


# engine = create_engine("sqlite:///:memory:")
# engine = create_engine("sqlite:///receipts.db")
# engine = create_engine("mysql://root:Tescomm%40123@mysql.i-tudou.com:3306/gas_management_system_real")
engine = create_engine("postgresql+psycopg2://postgres:aXoMMebXwmXPgrlCDAI6ulqF6@10.0.36.13:5432/potato_geo_element")
# metadata_obj = MetaData()
#
# # create city SQL table
# table_name = "receipts"
# receipts = Table(
#     table_name,
#     metadata_obj,
#     Column("receipt_id", Integer, primary_key=True),
#     Column("customer_name", String(16), primary_key=True),
#     Column("price", Float),
#     Column("tip", Float),
# )
# metadata_obj.create_all(engine)
#
# rows = [
#     {"receipt_id": 1, "customer_name": "Alan Payne", "price": 12.06, "tip": 1.20},
#     {"receipt_id": 2, "customer_name": "Alex Mason", "price": 23.86, "tip": 0.24},
#     {"receipt_id": 3, "customer_name": "Woodrow Wilson", "price": 53.43, "tip": 5.43},
#     {"receipt_id": 4, "customer_name": "Margaret James", "price": 21.11, "tip": 1.00},
# ]
# for row in rows:
#     stmt = insert(receipts).values(**row)
#     with engine.begin() as connection:
#         cursor = connection.execute(stmt)

inspector = inspect(engine)
columns_info = [(col["name"], col["type"], col["comment"]) for col in inspector.get_columns("risk_info")]

table_description = "TableName: resi_info\n Columns:\n" + "\n".join([f"  - {name}: {col_type}: {comment}" for name, col_type, comment in columns_info])
print(table_description)

from smolagents import tool, OpenAIServerModel


@tool
def sql_engine(query: str) -> str:
    """
    Allows you to perform SQL queries on the table. Returns a string representation of the result.
    The table is named 'risk_info'. Its description is as follows:
    Columns:
      - risk_info_id: BIGINT: 主键id
      - risk_type_id: BIGINT: risk_type表隐患类型id
      - risk_type_level_id: BIGINT: 隐患分类等级id
      - risk_code: VARCHAR(32) COLLATE "utf8_general_ci": 隐患编号
      - risk_level: VARCHAR(100) COLLATE "utf8_general_ci": 隐患建议级别（{1: "重大隐患",2: "较大隐患",3: "一般隐患"}）
      - found_date: VARCHAR(32) COLLATE "utf8_general_ci": 隐患发现时间
      - risk_detail: VARCHAR(1024) COLLATE "utf8_general_ci": 隐患详情描述
      - device_type: VARCHAR(100) COLLATE "utf8_general_ci": 设备类型
      - device_code: VARCHAR(255) COLLATE "utf8_general_ci": 设备编码
      - device_name: VARCHAR(255) COLLATE "utf8_general_ci": 设备设施名称
      - area: VARCHAR(25) COLLATE "utf8_general_ci": 所属区
      - street: VARCHAR(25) COLLATE "utf8_general_ci": 所属街道
      - address: VARCHAR(1024) COLLATE "utf8_general_ci": 地点
      - coordinate_x: VARCHAR(32) COLLATE "utf8_general_ci": 坐标X
      - coordinate_y: VARCHAR(32) COLLATE "utf8_general_ci": 坐标Y
      - pipeline_x: VARCHAR(32) COLLATE "utf8_general_ci": 管线坐标X
      - pipeline_y: VARCHAR(32) COLLATE "utf8_general_ci": 管线坐标Y
      - manage_unit: BIGINT: 管理责任单位
      - manage_unit_person: VARCHAR(32) COLLATE "utf8_general_ci": 单位责任人
      - plan_clear_date: VARCHAR(32) COLLATE "utf8_general_ci": 计划消除时间
      - real_eliminate_time: VARCHAR(32) COLLATE "utf8_general_ci": 实际消除时间
      - project_code: VARCHAR(64) COLLATE "utf8_general_ci": 工程项目号
      - construction_unit: VARCHAR(64) COLLATE "utf8_general_ci": 施工单位
      - supervise_unit: VARCHAR(64) COLLATE "utf8_general_ci": 监理单位
      - use_gas_type: VARCHAR(64) COLLATE "utf8_general_ci": 用气性质
      - gas_limit_stop: VARCHAR(100) COLLATE "utf8_general_ci": 限购/停气
      - govern_status: VARCHAR(100) COLLATE "utf8_general_ci": 治理情况
      - govern_measures: VARCHAR(255) COLLATE "utf8_general_ci": 治理措施
      - property_right: VARCHAR(100) COLLATE "utf8_general_ci": 产权性质
      - property_right_unit: BIGINT: 产权单位
      - rectifi_responsible_unit: BIGINT: 整改责任单位
      - build_date: VARCHAR(32) COLLATE "utf8_general_ci": 建设时间
      - coating_test_result: VARCHAR(100) COLLATE "utf8_general_ci": 防腐涂层检测结果
      - severity_type: VARCHAR(100) COLLATE "utf8_general_ci": 按后果严重性进行分类
      - is_in_cell: VARCHAR(100) COLLATE "utf8_general_ci": 是否在小区内
      - cell_name: VARCHAR(255) COLLATE "utf8_general_ci": 小区名称
      - area_street_person: VARCHAR(32) COLLATE "utf8_general_ci": 与区县对接联系人
      - remark: VARCHAR(1000) COLLATE "utf8_general_ci": 备注
      - occupy_area: VARCHAR(32) COLLATE "utf8_general_ci": 占压物面积
      - occupy_use: VARCHAR(32) COLLATE "utf8_general_ci": 占压物用途
      - occupy_unit: VARCHAR(255) COLLATE "utf8_general_ci": 占压单位/个人名称
      - occupy_unit_type: VARCHAR(100) COLLATE "utf8_general_ci": 占压单位性质
      - occupy_phone: VARCHAR(32) COLLATE "utf8_general_ci": 占压物联系电话
      - occupy_build_date: VARCHAR(32) COLLATE "utf8_general_ci": 占压物建设时间
      - occupy_desc: VARCHAR(64) COLLATE "utf8_general_ci": 占压物描述
      - has_person_activite: VARCHAR(100) COLLATE "utf8_general_ci": 有无经常性人员活动
      - with_relocation: VARCHAR(100) COLLATE "utf8_general_ci": 是否具备移改条件
      - pipe_depth: VARCHAR(32) COLLATE "utf8_general_ci": 管线埋深
      - pipe_diameter: VARCHAR(128) COLLATE "utf8_general_ci": 管径
      - pipe_pressure: VARCHAR(32) COLLATE "utf8_general_ci": 管线压力
      - pipe_occupy_length: VARCHAR(128) COLLATE "utf8_general_ci": 占压管线长度
      - pipe_build_date: VARCHAR(32) COLLATE "utf8_general_ci": 管线建设时间
      - cross_name: VARCHAR(64) COLLATE "utf8_general_ci": 穿越物名称
      - crossed_owner_unit: VARCHAR(64) COLLATE "utf8_general_ci": 被穿越物权属单位
      - cross_person: VARCHAR(32) COLLATE "utf8_general_ci": 穿越物联系人
      - cross_phone: VARCHAR(32) COLLATE "utf8_general_ci": 穿越物联系方式
      - locale_imgs: VARCHAR(500) COLLATE "utf8_general_ci": 现场示意图
      - pre_imgs: VARCHAR(3000) COLLATE "utf8_general_ci": 隐患消除前照片
      - after_imgs: VARCHAR(500) COLLATE "utf8_general_ci": 隐患消除后照片
      - risk_source: VARCHAR(100) COLLATE "utf8_general_ci": 隐患来源
      - fill_unit: BIGINT: 填报单位
      - fill_person: VARCHAR(32) COLLATE "utf8_general_ci": 填报人
      - checkin_date: VARCHAR(32) COLLATE "utf8_general_ci": 登记时间
      - suggest_technical_improve: CHAR(10) COLLATE "utf8_general_ci": 是否推荐技改
      - approval_status: VARCHAR(8) COLLATE "utf8_general_ci": 审批状态
      - approve_template_code: VARCHAR(32) COLLATE "utf8_general_ci": 审批流程模板
      - eliminate_summary_id: VARCHAR(32) COLLATE "utf8_general_ci": 隐患消除审批流程单据id
      - add_technical_improve: CHAR(10) COLLATE "utf8_general_ci": 技改状态
      - summary_id: VARCHAR(32) COLLATE "utf8_general_ci": 审批流程单据id
      - create_by: BIGINT: 创建人
      - update_by: BIGINT: 更新人
      - create_time: VARCHAR(100): 创建时间
      - update_time: VARCHAR(100): 更新时间
      - create_dept: BIGINT: 创建部门
      - update_dept: BIGINT: 更新部门
      - eliminate_approval_status: VARCHAR(8) COLLATE "utf8_general_ci": 隐患消除审批状态
      - eliminate_approve_template_code: VARCHAR(32) COLLATE "utf8_general_ci": 隐患消除审批流程模板
      - del_flag: CHAR(10) COLLATE "utf8_general_ci": 删除标志
      - risk_old_code: VARCHAR(32) COLLATE "utf8_general_ci": 旧数据隐患编号
      - acceptance_desc: VARCHAR(512) COLLATE "utf8_general_ci": 验收情况描述
      - acceptance_conclusion: VARCHAR(512) COLLATE "utf8_general_ci": 验收结论

    Args:
        query: The query to perform. This should be correct SQL.

    return:
       sql执行的结果
    """
    output = ""
    with engine.connect() as con:
        rows = con.execute(text(query))
        for row in rows:
            output += "\n" + str(row)

    print(output)
    return output


from smolagents import CodeAgent

model = OpenAIServerModel(
    model_id="DeepSeek-R1-Distill-Qwen-32B",
    api_base="http://ai-api.e-tudou.com:9000/v1/",  # Leave this blank to query OpenAI servers.
    api_key='sk-uG93vRV5V2Dog95J15FfCdE5DaAe438fBb17C642F2E1Ae57',  # Switch to the API key for the server you're targeting.
)

agent = CodeAgent(
    tools=[sql_engine],
    model=model,
)

# agent.run("查询risk_level=2的隐患信息的数量")
agent.run("检索全部risk_level为1的隐患数据有多少条")

# from smolagents import GradioUI

# GradioUI(agent).launch()
