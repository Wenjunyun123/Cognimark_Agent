# 数据预处理系统设计文档

**日期**: 2025-01-24
**作者**: Claude + 用户
**状态**: 已批准

## 1. 概述

### 1.1 背景
当前数据导入系统直接将Excel/CSV数据写入数据库，缺乏统一的标准化格式和原始数据保留机制。需要建立标准化的预处理系统，解决数据质量不一致问题。

### 1.2 目标
- 建立标准化的4字段数据格式（id, 更新时间, 资源名称, 资源链接）
- 保留完整原始商品信息用于追溯
- 最小化前后端改动，确保系统兼容性

## 2. 数据模型设计

### 2.1 核心标准格式（ProductDB - 现有表）

| 字段 | 类型 | 说明 | 必填 |
|------|------|------|------|
| external_id | String(100) | 外部唯一标识符（资源编号） | ✅ |
| updated_at | DateTime | 资源最后更新时间 | ✅ |
| title_zh | String(500) | 资源名称（中文名称） | ✅ |
| resource_url | String(1000) | 资源链接地址 | ✅ |
| product_id | String(50) | 内部主键（UUID） | 自动 |
| resource_type | String(50) | 资源类型（baidu_pan/quark/aliyun等） | 自动检测 |

### 2.2 原始商品信息表（RawProductDataDB - 新增）

```python
class RawProductDataDB(Base):
    """原始商品信息表 - 存储P00x等完整原始数据"""
    __tablename__ = "raw_product_data"

    id = Column(String(50), primary_key=True)  # UUID
    external_id = Column(String(100), nullable=False, index=True)  # 关联ProductDB
    raw_data = Column(Text, nullable=False)  # JSON格式存储完整原始数据
    source_file = Column(String(500))  # 来源文件名
    source_row = Column(Integer)  # 原始行号
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_raw_external_id', 'external_id'),
    )
```

**关联关系**:
- `RawProductDataDB.external_id` → `ProductDB.external_id`
- 一对一关系：每个标准化商品对应一条原始数据记录

## 3. 列映射配置

### 3.1 自动检测规则

| 标准字段 | 可能的原始列名（模糊匹配） |
|----------|---------------------------|
| external_id | ID, 编号, 资源ID, 资源编号, id |
| updated_at | 更新时间, 时间, 日期, 更新日期, date, time, updated |
| title_zh | 资源名称, 名称, 标题, 商品名称, 课程名称, title, name |
| resource_url | 资源链接, 链接, url, URL, 地址, 下载地址, 网盘地址 |

### 3.2 映射策略
1. **精确匹配** - 列名完全相同
2. **包含匹配** - 列名包含关键词（不区分大小写）
3. **别名匹配** - 预定义的别名列表
4. **位置匹配** - 对于无名列，按位置映射（后备方案）

## 4. 数据验证规则

### 4.1 必填字段验证
- `external_id`: 不能为空或None
- `title_zh`: 不能为空或None
- `resource_url`: 不能为空或None，且必须是有效URL格式

### 4.2 数据类型验证
- `external_id`: 转换为字符串，去除首尾空格
- `updated_at`: 尝试解析为datetime，失败则使用当前时间
- `title_zh`: 字符串，最大长度500
- `resource_url`: 字符串，最大长度1000，URL格式验证

### 4.3 去重验证
- `external_id`在当前批次内必须唯一
- 与数据库已有记录的`external_id`对比：
  - 如果`skip_duplicates=True`，跳过重复记录
  - 如果`update_existing=True`，更新现有记录

## 5. API接口设计

### 5.1 现有API（保持不变）

```
POST /import/data
- 功能: 导入Excel/CSV数据
- 输入: file (UploadFile), skip_duplicates, update_existing, batch_name, column_mapping
- 输出: ImportResponse (batch_id, total_records, success_count, failed_count, skipped_count, errors)
- 变更: 内部同时写入ProductDB和RawProductDataDB
```

### 5.2 新增API

```
GET /courses/{course_id}/detail
- 功能: 获取商品详情（包含原始数据）
- 输出: { standard: {...}, raw_data: {...} }
```

## 6. 实现方案

### 6.1 数据库变更
1. 在`database/models.py`中新增`RawProductDataDB`模型
2. 执行数据库迁移创建`raw_product_data`表

### 6.2 导入服务变更
修改`services/import_service.py`:
- 在`_import_dataframe`方法中，同时写入两张表
- 保存完整原始行数据到`raw_data`字段（JSON格式）

### 6.3 CRUD操作变更
在`database/crud.py`中新增:
- `RawProductDataCRUD`类
- `get_raw_data_by_external_id`方法

### 6.4 API变更
在`backend/api.py`中:
- 修改`/import/data`端点，同时写入两张表
- 新增`GET /courses/{course_id}/detail`端点

## 7. 前端兼容性

✅ **无需改动** - 前端现有API调用保持不变：
- `uploadExcel()` - 上传文件
- `/import/data` - 导入数据
- `/courses/search` - 搜索课程

可选增强：
- 商品详情页可添加"查看原始数据"折叠面板
- 显示`raw_data`中的完整原始字段

## 8. 实施步骤

1. ✅ 设计评审通过
2. ⬜ 新增`RawProductDataDB`模型
3. ⬜ 修改`import_service.py`支持双表写入
4. ⬜ 新增CRUD操作
5. ⬜ 新增查询API端点
6. ⬜ 数据库迁移测试
7. ⬜ 端到端测试
8. ⬜ 文档更新

## 9. 后续优化方向

1. **预处理报告** - 在入库前生成数据质量报告供人工review
2. **配置化映射** - 支持通过配置文件定义列映射规则
3. **数据血缘** - 记录数据来源、处理历史
4. **版本控制** - 支持数据更新历史追溯
5. **批量操作优化** - 使用bulk insert提升性能
