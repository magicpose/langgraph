from langchain.tools import tool
import requests
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


ddl_test = [" -- 隐患信息表\nCREATE TABLE `bdc_exception`  (\n  `exception_id` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '主键id',\n  `exception_code` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '异常编号',\n  `exception_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '异常标题',\n  `exception_source` varchar(2) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '异常来源 1.管线运行 2.调压站运行 3.调压箱运行 4.施工配合',\n  `exception_addresses` varchar(512) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '异常地点',\n  `exception_category` enum('1','2','3','4','5','6') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '异常分类 1 调压站 2 调压箱 3 管线 4 闸井 5 阴保设施 6.施工配合',\n  `exception_type` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '异常类型',\n  `exception_level` int NULL DEFAULT NULL COMMENT '异常等级 0：紧急 1：严重 2：一般',\n  `report_user` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '上报人',\n  `report_order` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '所属机构',\n  `find_time` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发现时间',\n  `report_time` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '上报时间',\n  `area_id` int NULL DEFAULT NULL COMMENT '行政区域 1 东城 2 西城 3 海淀 4 朝阳 5 昌平 6 顺义 7 大兴 8 丰台 9 怀柔 10 密云 11 石景山 12 门头沟 13 通州 14 平谷 15 延庆 16 房山',\n  `street_name` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '街道名称',\n  `contact` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '联系人',\n  `contact_phone` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '联系方式',\n  `lng` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '经度',\n  `lat` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '纬度',\n  `scene_deal_state` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '现场处理情况',\n  `is_close` int NULL DEFAULT NULL COMMENT '异常是否关闭',\n  `deal_user` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '异常处理人',\n  `deal_time` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '异常关闭时间',\n  `is_delete` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '是否删除',\n  `update_user` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '修改人',\n  `update_time` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '修改时间',\n  `update_org` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '修改机构',\n  `monitor_model` int NULL DEFAULT NULL COMMENT '监控方式 1：按运行周期 2：一天一次 3：旁站',\n  `elimination_mode` int NULL DEFAULT NULL COMMENT '消除方式 1：现场处置 2：维检修 3：泄漏检测 4：第三方处置 5：抢修 6：技改',\n  `whether_monitor` int NULL DEFAULT NULL COMMENT '是否发布监控任务单 1 是，0 否',\n  `whether_elimination` int NULL DEFAULT NULL COMMENT '是否发布消除任务单 1 是，0 否',\n  `whether_single_dispose` int NULL DEFAULT NULL COMMENT '是否单人处置 1 是，0 否',\n  `exception_scope` varchar(2000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '异常范围',\n  `device_name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '设备名称',\n  `device_code` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '设备编号',\n  `device_bitno` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '设备位号',\n  `run_model` varchar(4000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '运行周期',\n  `single_dispose_check` int NULL DEFAULT NULL COMMENT '单人处置审核',\n  `close_check` int NULL DEFAULT NULL COMMENT '异常关闭审核',\n  `deal_annex` varchar(300) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '照片/录像弃用',\n  `business_id` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '所属业务的任务id',\n  `video` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '录像',\n  `picture` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '图片',\n  `eliminate_img` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '消除后照片',\n  `add_monitor_flag` int NULL DEFAULT NULL COMMENT '新增监控工单状态 1 可新增 0 不能新增',\n  `add_elimination_flag` int NULL DEFAULT NULL COMMENT '新增处置工单状态 1 可新增 0 不能新增',\n  PRIMARY KEY (`exception_id`) USING BTREE\n) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '异常信息表' ROW_FORMAT = DYNAMIC;\n", " -- 异常审核表\nCREATE TABLE `bdc_exception_check` (\n  `check_id` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '审核ID',\n  `business_id` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '审核主体id',\n  `check_type` int DEFAULT NULL COMMENT '审核类型 1 单人处置审核，2 监控任务审核,3 消除任务审核，4 监控记录审核，5 消除记录审核，6 异常关闭审核',\n  `check_status` int DEFAULT NULL COMMENT '审核状态 1、审核通过 2、驳回',\n  `check_user` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '审核人',\n  `check_org` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '审核人组织机构',\n  `check_time` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '审核时间',\n  `check_opinion` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '审核意见',\n  `check_user_role` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '审核人角色',\n  `create_user` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '创建人',\n  `create_time` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '创建时间',\n  PRIMARY KEY (`check_id`) USING BTREE\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC COMMENT='异常审核表';\n", " -- 异常详情表\nCREATE TABLE `bdc_exception_detail` (\n  `detail_id` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '详情id',\n  `exception_id` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '异常id',\n  `check_item` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '检查项',\n  `check_item_code` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '检查项编号',\n  `status` int DEFAULT NULL COMMENT '状态 0：是 1：否',\n  `remark` varchar(2048) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '描述',\n  `parent_id` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '详情父id',\n  PRIMARY KEY (`detail_id`) USING BTREE\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC COMMENT='异常详情表';\n", " -- 监控/消除记录表\nCREATE TABLE `bdc_monitor_eliminate_record` (\n  `record_id` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '记录id',\n  `task_id` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '任务id',\n  `report_user` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '填报人员',\n  `start_time` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '开始时间',\n  `end_time` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '结束时间',\n  `record_status` int DEFAULT NULL COMMENT '处置状态',\n  `record_remark` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '处置描述',\n  `record_type` int DEFAULT NULL COMMENT '记录类别 1 监控记录 2 消除记录',\n  `class_check_status` int DEFAULT NULL COMMENT '班长审核状态 1通过 2不通过',\n  `class_check_opinion` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '班长审核意见',\n  `create_user` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '创建人',\n  `create_org` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '创建人部门',\n  `create_time` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '创建时间',\n  `update_user` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '更新人',\n  `update_time` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '更新时间',\n  `update_org` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '更新人部门',\n  `delete_flag` int DEFAULT NULL COMMENT '删除状态 0未删除 1已删除',\n  `whether_controlled` int DEFAULT NULL COMMENT '是否受控 1 是 0 否',\n  `deal_annex` varchar(300) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '照片/录像',\n  `video` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '录像',\n  `picture` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '照片',\n  `business_id` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '业务记录id',\n  `director_check_status` int DEFAULT NULL COMMENT '所长审核状态',\n  `director_check_opinion` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '所长审核描述',\n  `third_party` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '第三方维修单位',\n  `third_party_user` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '第三方维修人员',\n  PRIMARY KEY (`record_id`) USING BTREE\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC COMMENT='监控/消除记录表';\n", " -- 监控/消除任务表\nCREATE TABLE `bdc_monitor_eliminate_task` (\n  `task_id` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '编号',\n  `exception_id` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '异常id',\n  `task_model` int DEFAULT NULL COMMENT '监控消除方式 监控（1：按运行周期 2：1天一次 3：旁站） 消除（1：现场处置 2：维检修 3：泄漏检测 4：第三方处置 5：抢修 6：技改）',\n  `task_type` int DEFAULT NULL COMMENT '任务类别 1 监控任务 2 消除任务',\n  `start_time` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '开始时间',\n  `end_time` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '结束时间',\n  `executor` varchar(330) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '执行人',\n  `create_user` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '创建人',\n  `create_org` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '创建人部门',\n  `create_time` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '创建时间',\n  `update_user` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '更新人',\n  `update_time` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '更新时间',\n  `update_org` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '更新人部门',\n  `delete_flag` int DEFAULT NULL COMMENT '删除状态 0 未删除 1 已删除',\n  `whether_history` int DEFAULT NULL COMMENT '是否历史 1 是，0 否',\n  `check_status` int DEFAULT NULL COMMENT '审核状态 1 通过 2 调整通过',\n  `check_opinion` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '审核意见',\n  `whether_temporary` int DEFAULT NULL COMMENT '是否临时 1 是，0 否',\n  `make_task` int DEFAULT NULL COMMENT '是否制定任务 1 是，0 否',\n  `monitor_affirm` int DEFAULT NULL COMMENT '班长确认 1 是，0 否',\n  `business_id` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '对应业务id 对应模块的任务id',\n  `task_status` int DEFAULT NULL COMMENT '任务状态 1 未开始 2 进行中 3 已完成',\n  `temporary_task_source` int DEFAULT NULL COMMENT '任务来源 1 中低压维检修 2 高压维检修 3 泄漏检测',\n  PRIMARY KEY (`task_id`) USING BTREE\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC COMMENT='监控/消除任务表';\n", " -- 隐患区域轨迹表\nCREATE TABLE `bdc_risk_area_trajectory` (\n  `id` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT 'id',\n  `object_id` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '对象id 管线隐患就是RiskPipeLine表id，还有调压站隐患和闸井隐患类似',\n  `risk_des_type` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '隐患目标类型，区分objectId是哪个类型隐患，并且可以判断riskType的内容 1管线2站箱3闸井',\n  `trajectory` varchar(4000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '轨迹',\n  `create_user` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '创建人',\n  `update_user` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '更新人',\n  `create_time` varchar(19) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '创建时间',\n  `update_time` varchar(19) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '更新时间',\n  `create_org` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '创建人',\n  `update_org` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '更新人',\n  PRIMARY KEY (`id`) USING BTREE\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC COMMENT='隐患区域轨迹表';\n", " -- 隐患审核表\nCREATE TABLE `bdc_risk_audit` (\n  `audit_id` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '主键',\n  `object_id` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '业务主键ID',\n  `check_org` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '审核机构',\n  `check_user` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '审核人',\n  `check_status` tinyint DEFAULT NULL COMMENT '审核状态 0：通过 1：不通过',\n  `check_opinion` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '审核意见',\n  `check_time` varchar(19) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '审核时间',\n  `audit_role_code` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '角色类型',\n  `risk_des_type` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '隐患目标类型，区分objectId是哪个类型隐患 1管线2站箱3闸井',\n  PRIMARY KEY (`audit_id`) USING BTREE\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC COMMENT='隐患审核表';\n", " -- 隐患信息基础表\nCREATE TABLE `bdc_risk_check_base` (\n  `check_id` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '排查id',\n  `org_id` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '管理单位',\n  `check_type` int DEFAULT NULL COMMENT '隐患排查类型 1 管线排查 2 闸井排查 3 调压站箱排查',\n  `risk_num` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '隐患编号',\n  `risk_name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '名称',\n  `risk_type` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '隐患类型',\n  `possibility` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '事故发生可能性',\n  `owner_type` int DEFAULT NULL COMMENT '权属类型',\n  `seriousness` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '事故后果严重性',\n  `risk_level` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '隐患等级',\n  `risk_region` int DEFAULT NULL COMMENT '所属区域',\n  `remove_date` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '计划消除时间',\n  `use_gas_type` int DEFAULT NULL COMMENT '用气性质',\n  `district` int DEFAULT NULL COMMENT '所属县区',\n  `address` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '所属位置',\n  `project_num` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '项目编号',\n  `result_type` int DEFAULT NULL COMMENT '整改方式',\n  `is_controll` int DEFAULT NULL COMMENT '是否可控',\n  `remark` varchar(2000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '备注',\n  `creator_id` int DEFAULT NULL COMMENT '创建人id',\n  `create_date` datetime DEFAULT NULL COMMENT '创建日期',\n  `creator_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '创建人姓名',\n  `street` varchar(400) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '所属街道',\n  `old_village` int DEFAULT NULL COMMENT '是否老旧小区',\n  `control_user` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '防控措施责任人',\n  `control_describe` varchar(2000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '防控措施描述',\n  `plan_describe` varchar(2000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '隐患预案描述',\n  `governance_org` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '治理责任单位',\n  `governance_describe` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '治理方案描述',\n  PRIMARY KEY (`check_id`) USING BTREE\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC COMMENT='隐患信息基础表';\n", " -- 管线排查\nCREATE TABLE `bdc_risk_check_pipe` (\n  `pipe_id` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '主键id',\n  `risk_base_id` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '隐患排查基础表',\n  `pipeline_type` varchar(400) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '管线铺设位置',\n  `material` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '材质',\n  `run_year` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '投运年代 区间形式 2014-2018',\n  `press_level` int DEFAULT NULL COMMENT '压力级制',\n  `pipe_diameter` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '管径',\n  `find_type` int DEFAULT NULL COMMENT '排查发现方式 数据字典对应',\n  `find_date` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '排查发现时间',\n  `describes` varchar(2000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '隐患描述',\n  `risk_plan` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '隐患预案附件',\n  `control_measures` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '防控措施附件',\n  `governance` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '治理方案附件',\n  `create_id` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '添加人id 当前用户ID',\n  `create_date` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建日期 默认为当前时间',\n  `status` varchar(2) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '隐患排查状态',\n  `other_remark` varchar(2000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '其他描述',\n  `pipe_start` varchar(400) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '起点',\n  `pipe_end` varchar(400) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '终点',\n  PRIMARY KEY (`pipe_id`) USING BTREE\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC COMMENT='管线排查';\n", " -- 调压站箱排查\nCREATE TABLE `bdc_risk_check_station_box` (\n  `station_box_id` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '主键',\n  `risk_base_id` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '排查基础表id',\n  `device_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '调压站箱编号',\n  `device_bit_no` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '调压站箱位号',\n  `start_use_info` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '投运年代',\n  `pressure_level` decimal(2,0) DEFAULT NULL COMMENT '压力级制',\n  `device_type` decimal(2,0) DEFAULT NULL COMMENT '调压站箱类别',\n  `audit_status` decimal(2,0) DEFAULT NULL COMMENT '审核状态',\n  `find_type` decimal(2,0) DEFAULT NULL COMMENT '排查发现方式 数据字典对应',\n  `find_date` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '排查发现时间',\n  `describes` varchar(2000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '隐患描述',\n  `risk_plan` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '隐患预案附件',\n  `control_measures` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '防控措施附件',\n  `governance` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '治理方案附件',\n  `use_status` decimal(5,0) DEFAULT NULL COMMENT '使用状态',\n  `device_flow` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '流量',\n  `device_brand` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '品牌',\n  `device_model` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '型号',\n  `use_date` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '启用时间',\n  `manager_type` decimal(5,0) DEFAULT NULL COMMENT '管理方式',\n  `is_monitor` decimal(2,0) DEFAULT NULL COMMENT '是否有监控',\n  `other_remark` varchar(2000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '其他描述',\n  `creator_id` int DEFAULT NULL COMMENT '创建人编号 当前用户ID',\n  `create_date` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建日期 默认为当前时间',\n  `location` decimal(5,0) DEFAULT NULL COMMENT '位置',\n  PRIMARY KEY (`station_box_id`) USING BTREE\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC COMMENT='调压站箱排查';\n", " -- 闸井排查\nCREATE TABLE `bdc_risk_check_well` (\n  `well_id` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '编号',\n  `risk_base_id` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '隐患排查基础表',\n  `del_flag` decimal(1,0) DEFAULT NULL COMMENT '删除标志 0未删除1已删除',\n  `device_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '闸井名称',\n  `device_code` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '闸井编号',\n  `device_bit_no` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '闸井位号',\n  `start_use_info` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '投运年代',\n  `device_pressure_level` decimal(2,0) DEFAULT NULL COMMENT '压力级制',\n  `gate_well_material` decimal(2,0) DEFAULT NULL COMMENT '材质',\n  `pipe_diameter` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '管径',\n  `risk_audit_status` decimal(2,0) DEFAULT NULL COMMENT '审核状态',\n  `gate_well_valve_type` decimal(2,0) DEFAULT NULL COMMENT '阀门类型',\n  `find_type` decimal(2,0) DEFAULT NULL COMMENT '排查发现方式 数据字典对应',\n  `find_date` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '排查发现时间',\n  `describes` varchar(2000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '隐患描述',\n  `risk_plan` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '隐患预案附件',\n  `control_measures` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '防控措施附件',\n  `is_direct_buried` decimal(2,0) DEFAULT NULL COMMENT '是否直埋',\n  `is_monitor` decimal(2,0) DEFAULT NULL COMMENT '是否有监控',\n  `governance` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '治理方案附件',\n  `create_user` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '创建人',\n  `create_time` datetime DEFAULT NULL COMMENT '创建时间',\n  `use_status` decimal(5,0) DEFAULT NULL COMMENT '使用状态',\n  `gate_well_type` decimal(5,0) DEFAULT NULL COMMENT '闸井形式 对应数据字典',\n  `use_date` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '启用时间',\n  `manager_type` decimal(4,0) DEFAULT NULL COMMENT '管理方式',\n  `other_remark` varchar(2000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '其他描述',\n  `location` decimal(2,0) DEFAULT NULL COMMENT '位置',\n  PRIMARY KEY (`well_id`) USING BTREE\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC COMMENT='闸井排查';\n"]

doc_test = ['exception_level枚举使用：异常等级 0：哈哈 1：拉拉 2：巴巴', 'street_name翻译为英文']
# @tool
def search_milvus(question: str, database_id: str = "479"):
    """在Milvus中搜索最相似的向量

    Args:
        question (str): 问题
        database_id (str): 数据库id

    Returns:
        list: 搜索结果列表
    """
    try:
        # 格式化结果
        resilt = {
            "question": [],
            "doc":doc_test,
            "ddl":ddl_test,
        }

        return resilt
    except Exception as e:
        return f"搜索出错: {str(e)}"


# @tool
def search_atlas(question: str, database_id: str = "479"):
    """ 查询数据库图谱信息

    Args:
        question (str): 问题
        database_id (str): 数据库id

    Returns:
        list: 搜索结果列表
    """

    try:
        result = {
            "question": [],
            "doc": [],
            "ddl": []
        }
        # 格式化结果
        return result
    except Exception as e:
        return f"搜索出错: {str(e)}"

# def run_sql(sql: str, database_id: str = "479"):
#     url = 'http://apisix-dev1.e-tudou.com:9080/copilot/v1/openapi/chat_db/runsql'
#
#     # 查询参数
#     params = {
#         'sql': sql,
#         'id': database_id,
#         'pageNo': '1',
#         'pageSize': '10',
#         'source': '0'
#     }
#
#     try:
#         # 发送 GET 请求
#         response = requests.get(url, params=params)
#
#         logger.info(f"request run_sql:{response.json()}")
#
#         # 检查响应
#         if response.status_code == 200 and response.json()['code'] == 1 and response.json()['data']['code'] == 1:
#             data = response.json()['data']['data']['data']['records']
#             return data
#         else:
#             if response.json()['data']['msg']:
#                 return response.json()['data']['msg']
#             return response.json()['data']['data']['msg']
#
#     except Exception as e:
#         logger.info(f"request run_sql error:{e}")
#         return f"运行sql失败,{e}"

def run_sql(sql: str, database_id: str = "479"):
    url = 'http://apisix-dev1.e-tudou.com:9080/copilot/v1/openapi/chat_db/runsql'

    # 请求体数据
    payload = {
        'sql': sql,
        'id': database_id,
        'pageNo': '1',
        'pageSize': '10',
        'source': '0'
    }

    try:
        # 发送 POST 请求
        response = requests.post(url, json=payload)

        logger.info(f"request run_sql:{response.json()}")

        # 检查响应
        if response.status_code == 200 and response.json()['code'] == 1 and response.json()['data']['code'] == 1:
            data = response.json()['data']['data']['data']['records']
            return data
        else:
            if response.json()['data']['msg']:
                return response.json()['data']['msg']
            return response.json()['data']['data']['msg']

    except Exception as e:
        logger.info(f"request run_sql error:{e}")
        return f"运行sql失败,{e}"


def search_database(database_id: str = "479"):
    url = f"http://apisix-dev1.e-tudou.com:9080/copilot/v1/openapi/kl_engine_datasource/db/{database_id}"

    try:
        response = requests.get(url)

        # 检查响应状态码
        if response.status_code == 200 and response.json()['code'] == 1:
            # logger.info(f"查询数据库详情:{str(response.json())}")
            # 返回响应内容
            return response.json()['data']  # 如果响应是 JSON 格式
        else:
            return None
    except Exception as e:
        print(f"请求发生错误: {e}")
        return None


if __name__ == '__main__':
    # print(run_sql(sql = """ SELECT * FROM bdc_exception; """, database_id = "479"))
    # print(run_sql(sql = "SELECT area, COUNT(*) AS risk_count FROM gas_management_system.risk_info GROUP BY area", database_id = "479"))

    print(search_database(database_id= "479"))
    # search_milvus(question="查询所有隐患", database_id="479")
