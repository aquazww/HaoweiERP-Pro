# 数据库表结构文档

## 一、表分类概览

| 分类 | 表数量 | 说明 |
|------|--------|------|
| 基础资料模块 | 6 | 计量单位、分类、仓库、供应商、客户、商品 |
| 采购管理模块 | 2 | 采购主单、采购明细 |
| 销售管理模块 | 2 | 销售主单、销售明细 |
| 库存管理模块 | 8 | 库存、流水、入库、出库、调整、调拨 |
| 财务管理模块 | 2 | 收付款记录、付款明细 |
| 系统管理模块 | 3 | 用户、角色、日志 |
| Django内置 | 7 | 认证、权限、Session等 |

---

## 二、基础资料模块 (basic)

### 2.1 biz_unit - 计量单位表

| 字段名 | 数据类型 | 约束 | 默认值 | 说明 |
|--------|----------|------|--------|------|
| id | INTEGER | PRIMARY KEY | 自增 | 主键 |
| name | VARCHAR(50) | NOT NULL, UNIQUE | - | 单位名称 |
| symbol | VARCHAR(10) | NOT NULL | - | 单位符号 |
| base_unit_id | BIGINT | FOREIGN KEY | NULL | 基准单位ID |
| conversion_factor | DECIMAL(10,4) | - | NULL | 换算系数 |
| is_active | BOOL | NOT NULL | TRUE | 是否启用 |
| created_by_id | BIGINT | FOREIGN KEY | NULL | 创建人ID |
| created_at | DATETIME | NOT NULL | 自动 | 创建时间 |
| updated_at | DATETIME | NOT NULL | 自动 | 更新时间 |

**索引：**
- `biz_unit_created_by_id_fdb056b3` (created_by_id)
- `biz_unit_base_unit_id_71817342` (base_unit_id)

**业务含义：** 存储商品的计量单位信息，支持单位换算。

---

### 2.2 biz_category - 商品分类表

| 字段名 | 数据类型 | 约束 | 默认值 | 说明 |
|--------|----------|------|--------|------|
| id | INTEGER | PRIMARY KEY | 自增 | 主键 |
| name | VARCHAR(100) | NOT NULL | - | 分类名称 |
| code | VARCHAR(50) | NOT NULL | - | 分类编码 |
| parent_id | BIGINT | FOREIGN KEY | NULL | 父分类ID |
| level | INTEGER | NOT NULL | 1 | 层级深度 |
| path | VARCHAR(500) | NOT NULL | - | 分类路径 |
| sort_order | INTEGER | NOT NULL | 0 | 排序号 |
| is_active | BOOL | NOT NULL | TRUE | 是否启用 |
| remark | VARCHAR(200) | NOT NULL | - | 备注 |
| created_by_id | BIGINT | FOREIGN KEY | NULL | 创建人ID |
| created_at | DATETIME | NOT NULL | 自动 | 创建时间 |
| updated_at | DATETIME | NOT NULL | 自动 | 更新时间 |

**索引：**
- `biz_category_parent_id_906adb5c` (parent_id)
- `biz_categor_level_1c22ed_idx` (level)
- `biz_categor_path_2e19be_idx` (path)

**业务含义：** 存储商品分类的树形结构，支持多级分类。

---

### 2.3 biz_warehouse - 仓库表

| 字段名 | 数据类型 | 约束 | 默认值 | 说明 |
|--------|----------|------|--------|------|
| id | INTEGER | PRIMARY KEY | 自增 | 主键 |
| name | VARCHAR(100) | NOT NULL | - | 仓库名称 |
| address | VARCHAR(200) | NOT NULL | - | 仓库地址 |
| contact | VARCHAR(50) | NOT NULL | - | 联系人 |
| phone | VARCHAR(20) | NOT NULL | - | 联系电话 |
| is_active | BOOL | NOT NULL | TRUE | 是否启用 |
| created_at | DATETIME | NOT NULL | 自动 | 创建时间 |
| updated_at | DATETIME | NOT NULL | 自动 | 更新时间 |

**业务含义：** 存储仓库基本信息，用于库存管理。

---

### 2.4 biz_supplier - 供应商表

| 字段名 | 数据类型 | 约束 | 默认值 | 说明 |
|--------|----------|------|--------|------|
| id | INTEGER | PRIMARY KEY | 自增 | 主键 |
| code | VARCHAR(50) | NOT NULL, UNIQUE | - | 供应商编码 |
| name | VARCHAR(100) | NOT NULL | - | 公司名称 |
| tax_no | VARCHAR(50) | NOT NULL | - | 税号 |
| address | VARCHAR(200) | NOT NULL | - | 地址 |
| contact | VARCHAR(50) | NOT NULL | - | 联系人 |
| phone | VARCHAR(20) | NOT NULL | - | 联系电话 |
| email | VARCHAR(254) | NOT NULL | - | 公司邮箱 |
| bank_name | VARCHAR(100) | NOT NULL | - | 开户银行 |
| bank_account | VARCHAR(50) | NOT NULL | - | 银行账号 |
| bank_branch_no | VARCHAR(50) | NOT NULL | - | 支行行号 |
| balance | DECIMAL(14,2) | NOT NULL | 0 | 应付余额 |
| remark | TEXT | NOT NULL | - | 备注信息 |
| status | INTEGER | NOT NULL | 1 | 状态(0:禁用,1:启用) |
| created_at | DATETIME | NOT NULL | 自动 | 创建时间 |
| updated_at | DATETIME | NOT NULL | 自动 | 更新时间 |

**索引：**
- `biz_supplie_code_c6d0fc_idx` (code)
- `biz_supplie_name_beed3e_idx` (name)

**业务含义：** 存储供应商信息，用于采购管理。

---

### 2.5 biz_customer - 客户表

| 字段名 | 数据类型 | 约束 | 默认值 | 说明 |
|--------|----------|------|--------|------|
| id | INTEGER | PRIMARY KEY | 自增 | 主键 |
| code | VARCHAR(50) | NOT NULL, UNIQUE | - | 客户编码 |
| name | VARCHAR(100) | NOT NULL | - | 公司名称 |
| tax_no | VARCHAR(50) | NOT NULL | - | 税号 |
| address | VARCHAR(200) | NOT NULL | - | 公司地址 |
| contact | VARCHAR(50) | NOT NULL | - | 联系人 |
| phone | VARCHAR(20) | NOT NULL | - | 联系电话 |
| email | VARCHAR(254) | NOT NULL | - | 公司邮箱 |
| bank_name | VARCHAR(100) | NOT NULL | - | 开户银行 |
| bank_account | VARCHAR(50) | NOT NULL | - | 银行账号 |
| bank_branch_no | VARCHAR(50) | NOT NULL | - | 支行行号 |
| balance | DECIMAL(14,2) | NOT NULL | 0 | 应收余额 |
| remark | TEXT | NOT NULL | - | 备注信息 |
| status | INTEGER | NOT NULL | 1 | 状态(0:禁用,1:启用) |
| created_at | DATETIME | NOT NULL | 自动 | 创建时间 |
| updated_at | DATETIME | NOT NULL | 自动 | 更新时间 |

**索引：**
- `biz_custome_code_be2f91_idx` (code)
- `biz_custome_name_ab754f_idx` (name)

**业务含义：** 存储客户信息，用于销售管理。

---

### 2.6 biz_goods - 商品表

| 字段名 | 数据类型 | 约束 | 默认值 | 说明 |
|--------|----------|------|--------|------|
| id | INTEGER | PRIMARY KEY | 自增 | 主键 |
| code | VARCHAR(50) | NOT NULL, UNIQUE | - | 商品编码 |
| name | VARCHAR(100) | NOT NULL | - | 商品名称 |
| category_id | BIGINT | FOREIGN KEY, NOT NULL | - | 商品分类ID |
| unit_id | BIGINT | FOREIGN KEY | NULL | 计量单位ID |
| unit_name | VARCHAR(20) | NOT NULL | - | 计量单位名称(冗余) |
| spec | VARCHAR(100) | NOT NULL | - | 规格 |
| barcode | VARCHAR(50) | NOT NULL | - | 条形码 |
| purchase_price | DECIMAL(12,2) | NOT NULL | 0 | 进货价 |
| sale_price | DECIMAL(12,2) | NOT NULL | 0 | 销售价 |
| retail_price | DECIMAL(12,2) | NOT NULL | 0 | 零售价 |
| min_stock | INTEGER | NOT NULL | 0 | 最低库存 |
| max_stock | INTEGER | NOT NULL | 0 | 最高库存 |
| status | INTEGER | NOT NULL | 1 | 状态(0:下架,1:上架) |
| remark | TEXT | NOT NULL | - | 备注 |
| created_at | DATETIME | NOT NULL | 自动 | 创建时间 |
| updated_at | DATETIME | NOT NULL | 自动 | 更新时间 |

**索引：**
- `biz_goods_code_52cde8_idx` (code)
- `biz_goods_name_df9b8e_idx` (name)
- `biz_goods_categor_0a025a_idx` (category_id)

**业务含义：** 存储商品基本信息，是ERP系统的核心数据。

---

## 三、采购管理模块 (purchase)

### 3.1 biz_purchase_order - 采购主单

| 字段名 | 数据类型 | 约束 | 默认值 | 说明 |
|--------|----------|------|--------|------|
| id | INTEGER | PRIMARY KEY | 自增 | 主键 |
| order_no | VARCHAR(30) | NOT NULL, UNIQUE | - | 采购单号 |
| supplier_id | BIGINT | FOREIGN KEY, NOT NULL | - | 供应商ID |
| warehouse_id | BIGINT | FOREIGN KEY, NOT NULL | - | 入库仓库ID |
| order_date | DATE | NOT NULL | 当前日期 | 采购日期 |
| total_amount | DECIMAL(14,2) | NOT NULL | 0 | 总金额 |
| paid_amount | DECIMAL(14,2) | NOT NULL | 0 | 已付金额 |
| status | VARCHAR(20) | NOT NULL | 'pending' | 状态 |
| remark | TEXT | NOT NULL | - | 备注 |
| created_by_id | BIGINT | FOREIGN KEY | NULL | 创建人ID |
| created_at | DATETIME | NOT NULL | 自动 | 创建时间 |
| updated_at | DATETIME | NOT NULL | 自动 | 更新时间 |

**状态说明：**
- pending: 待入库
- partial: 部分入库
- completed: 已入库
- cancelled: 已取消

---

### 3.2 biz_purchase_item - 采购明细

| 字段名 | 数据类型 | 约束 | 默认值 | 说明 |
|--------|----------|------|--------|------|
| id | INTEGER | PRIMARY KEY | 自增 | 主键 |
| order_id | BIGINT | FOREIGN KEY, NOT NULL | - | 采购单ID |
| goods_id | BIGINT | FOREIGN KEY, NOT NULL | - | 商品ID |
| quantity | DECIMAL(12,2) | NOT NULL | - | 数量 |
| received_quantity | DECIMAL(12,2) | NOT NULL | 0 | 已入库数量 |
| price | DECIMAL(12,2) | NOT NULL | - | 单价 |
| amount | DECIMAL(14,2) | NOT NULL | - | 金额 |
| remark | VARCHAR(200) | NOT NULL | - | 备注 |

**约束：**
- UNIQUE(order_id, goods_id) - 同一采购单中商品不能重复

---

## 四、销售管理模块 (sale)

### 4.1 biz_sale_order - 销售主单

| 字段名 | 数据类型 | 约束 | 默认值 | 说明 |
|--------|----------|------|--------|------|
| id | INTEGER | PRIMARY KEY | 自增 | 主键 |
| order_no | VARCHAR(30) | NOT NULL, UNIQUE | - | 销售单号 |
| customer_id | BIGINT | FOREIGN KEY, NOT NULL | - | 客户ID |
| warehouse_id | BIGINT | FOREIGN KEY, NOT NULL | - | 出库仓库ID |
| order_date | DATE | NOT NULL | 当前日期 | 销售日期 |
| total_amount | DECIMAL(14,2) | NOT NULL | 0 | 总金额 |
| received_amount | DECIMAL(14,2) | NOT NULL | 0 | 已收金额 |
| status | VARCHAR(20) | NOT NULL | 'pending' | 状态 |
| remark | TEXT | NOT NULL | - | 备注 |
| created_by_id | BIGINT | FOREIGN KEY | NULL | 创建人ID |
| created_at | DATETIME | NOT NULL | 自动 | 创建时间 |
| updated_at | DATETIME | NOT NULL | 自动 | 更新时间 |

---

### 4.2 biz_sale_item - 销售明细

| 字段名 | 数据类型 | 约束 | 默认值 | 说明 |
|--------|----------|------|--------|------|
| id | INTEGER | PRIMARY KEY | 自增 | 主键 |
| order_id | BIGINT | FOREIGN KEY, NOT NULL | - | 销售单ID |
| goods_id | BIGINT | FOREIGN KEY, NOT NULL | - | 商品ID |
| quantity | DECIMAL(12,2) | NOT NULL | - | 数量 |
| shipped_quantity | DECIMAL(12,2) | NOT NULL | 0 | 已出库数量 |
| price | DECIMAL(12,2) | NOT NULL | - | 单价 |
| amount | DECIMAL(14,2) | NOT NULL | - | 金额 |
| remark | VARCHAR(200) | NOT NULL | - | 备注 |

---

## 五、库存管理模块 (inventory)

### 5.1 biz_inventory - 当前库存表

| 字段名 | 数据类型 | 约束 | 默认值 | 说明 |
|--------|----------|------|--------|------|
| id | INTEGER | PRIMARY KEY | 自增 | 主键 |
| goods_id | BIGINT | FOREIGN KEY, NOT NULL | - | 商品ID |
| warehouse_id | BIGINT | FOREIGN KEY, NOT NULL | - | 仓库ID |
| quantity | DECIMAL(12,2) | NOT NULL | 0 | 库存数量 |
| created_at | DATETIME | NOT NULL | 自动 | 创建时间 |
| updated_at | DATETIME | NOT NULL | 自动 | 更新时间 |

**约束：**
- UNIQUE(goods_id, warehouse_id) - 同一商品在同一仓库只有一条记录

---

### 5.2 biz_inventory_log - 库存流水表

| 字段名 | 数据类型 | 约束 | 默认值 | 说明 |
|--------|----------|------|--------|------|
| id | INTEGER | PRIMARY KEY | 自增 | 主键 |
| goods_id | BIGINT | FOREIGN KEY, NOT NULL | - | 商品ID |
| warehouse_id | BIGINT | FOREIGN KEY, NOT NULL | - | 仓库ID |
| change_type | VARCHAR(20) | NOT NULL | - | 变动类型 |
| change_quantity | DECIMAL(12,2) | NOT NULL | - | 变动数量 |
| before_quantity | DECIMAL(12,2) | NOT NULL | - | 变动前数量 |
| after_quantity | DECIMAL(12,2) | NOT NULL | - | 变动后数量 |
| related_order_type | VARCHAR(50) | NOT NULL | - | 关联单据类型 |
| related_order_id | INTEGER | NULL | NULL | 关联单据ID |
| remark | VARCHAR(200) | NOT NULL | - | 备注 |
| created_by_id | BIGINT | FOREIGN KEY | NULL | 操作人ID |
| created_at | DATETIME | NOT NULL | 自动 | 操作时间 |

**变动类型：**
- inbound: 入库
- outbound: 出库
- adjust: 库存调整
- check: 盘点

---

### 5.3 biz_stock_in - 入库单

| 字段名 | 数据类型 | 约束 | 默认值 | 说明 |
|--------|----------|------|--------|------|
| id | INTEGER | PRIMARY KEY | 自增 | 主键 |
| order_no | VARCHAR(30) | NOT NULL, UNIQUE | - | 入库单号 |
| purchase_order_id | BIGINT | FOREIGN KEY | NULL | 关联采购单ID |
| warehouse_id | BIGINT | FOREIGN KEY, NOT NULL | - | 仓库ID |
| total_amount | DECIMAL(14,2) | NOT NULL | 0 | 总金额 |
| status | VARCHAR(20) | NOT NULL | 'draft' | 状态 |
| remark | TEXT | NOT NULL | - | 备注 |
| created_by_id | BIGINT | FOREIGN KEY | NULL | 创建人ID |
| created_at | DATETIME | NOT NULL | 自动 | 创建时间 |
| confirmed_at | DATETIME | NULL | NULL | 确认时间 |

---

### 5.4 biz_stock_out - 出库单

| 字段名 | 数据类型 | 约束 | 默认值 | 说明 |
|--------|----------|------|--------|------|
| id | INTEGER | PRIMARY KEY | 自增 | 主键 |
| order_no | VARCHAR(30) | NOT NULL, UNIQUE | - | 出库单号 |
| sale_order_id | BIGINT | FOREIGN KEY | NULL | 关联销售单ID |
| warehouse_id | BIGINT | FOREIGN KEY, NOT NULL | - | 仓库ID |
| total_amount | DECIMAL(14,2) | NOT NULL | 0 | 总金额 |
| status | VARCHAR(20) | NOT NULL | 'draft' | 状态 |
| remark | TEXT | NOT NULL | - | 备注 |
| created_by_id | BIGINT | FOREIGN KEY | NULL | 创建人ID |
| created_at | DATETIME | NOT NULL | 自动 | 创建时间 |
| confirmed_at | DATETIME | NULL | NULL | 确认时间 |

---

### 5.5 biz_stock_adjust - 库存调整单

| 字段名 | 数据类型 | 约束 | 默认值 | 说明 |
|--------|----------|------|--------|------|
| id | INTEGER | PRIMARY KEY | 自增 | 主键 |
| order_no | VARCHAR(30) | NOT NULL, UNIQUE | - | 调整单号 |
| warehouse_id | BIGINT | FOREIGN KEY, NOT NULL | - | 仓库ID |
| adjust_type | VARCHAR(20) | NOT NULL | - | 调整类型 |
| reason | VARCHAR(20) | NOT NULL | - | 调整原因 |
| status | VARCHAR(20) | NOT NULL | 'draft' | 状态 |
| remark | TEXT | NOT NULL | - | 备注 |
| created_by_id | BIGINT | FOREIGN KEY | NULL | 创建人ID |
| created_at | DATETIME | NOT NULL | 自动 | 创建时间 |
| confirmed_at | DATETIME | NULL | NULL | 确认时间 |

---

### 5.6 biz_stock_adjust_item - 库存调整明细

| 字段名 | 数据类型 | 约束 | 默认值 | 说明 |
|--------|----------|------|--------|------|
| id | INTEGER | PRIMARY KEY | 自增 | 主键 |
| adjust_id | BIGINT | FOREIGN KEY, NOT NULL | - | 调整单ID |
| goods_id | BIGINT | FOREIGN KEY, NOT NULL | - | 商品ID |
| before_quantity | DECIMAL(12,2) | NOT NULL | - | 调整前数量 |
| adjust_quantity | DECIMAL(12,2) | NOT NULL | - | 调整数量 |
| after_quantity | DECIMAL(12,2) | NOT NULL | - | 调整后数量 |
| remark | VARCHAR(200) | NOT NULL | - | 备注 |

---

### 5.7 biz_stock_transfer - 库存调拨单

| 字段名 | 数据类型 | 约束 | 默认值 | 说明 |
|--------|----------|------|--------|------|
| id | INTEGER | PRIMARY KEY | 自增 | 主键 |
| order_no | VARCHAR(30) | NOT NULL, UNIQUE | - | 调拨单号 |
| from_warehouse_id | BIGINT | FOREIGN KEY, NOT NULL | - | 调出仓库ID |
| to_warehouse_id | BIGINT | FOREIGN KEY, NOT NULL | - | 调入仓库ID |
| status | VARCHAR(20) | NOT NULL | 'draft' | 状态 |
| remark | TEXT | NOT NULL | - | 备注 |
| created_by_id | BIGINT | FOREIGN KEY | NULL | 创建人ID |
| created_at | DATETIME | NOT NULL | 自动 | 创建时间 |
| confirmed_at | DATETIME | NULL | NULL | 确认时间 |

---

### 5.8 biz_stock_transfer_item - 库存调拨明细

| 字段名 | 数据类型 | 约束 | 默认值 | 说明 |
|--------|----------|------|--------|------|
| id | INTEGER | PRIMARY KEY | 自增 | 主键 |
| transfer_id | BIGINT | FOREIGN KEY, NOT NULL | - | 调拨单ID |
| goods_id | BIGINT | FOREIGN KEY, NOT NULL | - | 商品ID |
| quantity | DECIMAL(12,2) | NOT NULL | - | 调拨数量 |
| remark | VARCHAR(200) | NOT NULL | - | 备注 |

---

## 六、财务管理模块 (finance)

### 6.1 biz_payment - 收付款记录表

| 字段名 | 数据类型 | 约束 | 默认值 | 说明 |
|--------|----------|------|--------|------|
| id | INTEGER | PRIMARY KEY | 自增 | 主键 |
| order_no | VARCHAR(30) | NOT NULL, UNIQUE | - | 单据编号 |
| type | VARCHAR(10) | NOT NULL | - | 类型(pay:付款/receive:收款) |
| related_order_type | VARCHAR(20) | NOT NULL | - | 关联单据类型 |
| related_order_id | INTEGER | NOT NULL | 0 | 关联单据ID |
| related_order_no | VARCHAR(30) | NOT NULL | - | 关联单据编号 |
| related_party_type | VARCHAR(50) | NOT NULL | - | 往来单位类型 |
| related_party_id | INTEGER | NOT NULL | 0 | 往来单位ID |
| related_party_name | VARCHAR(100) | NOT NULL | - | 往来单位名称 |
| total_amount | DECIMAL(14,2) | NOT NULL | 0 | 总金额 |
| paid_amount | DECIMAL(14,2) | NOT NULL | 0 | 已付金额 |
| payment_method | VARCHAR(50) | NOT NULL | - | 付款方式 |
| payment_date | DATE | NULL | NULL | 付款日期 |
| status | VARCHAR(20) | NOT NULL | 'pending' | 状态 |
| remark | TEXT | NOT NULL | - | 备注 |
| created_by_id | BIGINT | FOREIGN KEY | NULL | 创建人ID |
| created_at | DATETIME | NOT NULL | 自动 | 创建时间 |
| confirmed_by_id | BIGINT | FOREIGN KEY | NULL | 确认人ID |
| confirmed_at | DATETIME | NULL | NULL | 确认时间 |

---

### 6.2 biz_payment_record - 付款记录明细

| 字段名 | 数据类型 | 约束 | 默认值 | 说明 |
|--------|----------|------|--------|------|
| id | INTEGER | PRIMARY KEY | 自增 | 主键 |
| payment_id | BIGINT | FOREIGN KEY, NOT NULL | - | 收付款单ID |
| amount | DECIMAL(14,2) | NOT NULL | - | 付款金额 |
| payment_method | VARCHAR(50) | NOT NULL | - | 付款方式 |
| payment_date | DATE | NOT NULL | - | 付款日期 |
| remark | TEXT | NOT NULL | - | 备注 |
| created_by_id | BIGINT | FOREIGN KEY | NULL | 操作人ID |
| created_at | DATETIME | NOT NULL | 自动 | 创建时间 |

---

## 七、系统管理模块 (system)

### 7.1 sys_user - 用户表

| 字段名 | 数据类型 | 约束 | 默认值 | 说明 |
|--------|----------|------|--------|------|
| id | INTEGER | PRIMARY KEY | 自增 | 主键 |
| username | VARCHAR(150) | NOT NULL, UNIQUE | - | 用户名 |
| password | VARCHAR(128) | NOT NULL | - | 密码(加密) |
| name | VARCHAR(50) | NOT NULL | - | 姓名 |
| phone | VARCHAR(20) | NOT NULL | - | 手机号 |
| email | VARCHAR(254) | NOT NULL | - | 邮箱 |
| avatar | VARCHAR(100) | NULL | NULL | 头像路径 |
| is_active | BOOL | NOT NULL | TRUE | 是否启用 |
| is_staff | BOOL | NOT NULL | FALSE | 是否员工 |
| is_superuser | BOOL | NOT NULL | FALSE | 是否超级用户 |
| permissions | JSON | NOT NULL | {} | 权限列表 |
| token_version | INTEGER | NOT NULL | 0 | Token版本号 |
| last_login | DATETIME | NULL | NULL | 最后登录时间 |
| date_joined | DATETIME | NOT NULL | 自动 | 注册时间 |
| created_at | DATETIME | NOT NULL | 自动 | 创建时间 |
| updated_at | DATETIME | NOT NULL | 自动 | 更新时间 |

---

### 7.2 sys_role - 角色表

| 字段名 | 数据类型 | 约束 | 默认值 | 说明 |
|--------|----------|------|--------|------|
| id | INTEGER | PRIMARY KEY | 自增 | 主键 |
| name | VARCHAR(50) | NOT NULL, UNIQUE | - | 角色名称 |
| permissions | JSON | NOT NULL | {} | 权限列表 |
| description | VARCHAR(200) | NOT NULL | - | 描述 |
| created_at | DATETIME | NOT NULL | 自动 | 创建时间 |
| updated_at | DATETIME | NOT NULL | 自动 | 更新时间 |

---

### 7.3 sys_log - 操作日志表

| 字段名 | 数据类型 | 约束 | 默认值 | 说明 |
|--------|----------|------|--------|------|
| id | INTEGER | PRIMARY KEY | 自增 | 主键 |
| user_id | BIGINT | FOREIGN KEY | NULL | 操作用户ID |
| action | VARCHAR(20) | NOT NULL | - | 操作类型 |
| module | VARCHAR(50) | NOT NULL | - | 操作模块 |
| detail | TEXT | NOT NULL | - | 操作详情 |
| ip_address | CHAR(39) | NULL | NULL | IP地址 |
| created_at | DATETIME | NOT NULL | 自动 | 操作时间 |

**操作类型：**
- create: 创建
- update: 更新
- delete: 删除
- login: 登录
- logout: 登出
- other: 其他

---

## 八、Django内置表

### 8.1 必需的Django表

| 表名 | 说明 | 必要性 |
|------|------|--------|
| django_migrations | 数据库迁移记录 | ✓ 必需 |
| django_session | 用户Session存储 | ✓ 必需 |
| django_content_type | 内容类型(用于GenericForeignKey) | ✓ 必需 |
| auth_permission | Django权限系统 | ✓ 必需 |

### 8.2 非必需的Django表

| 表名 | 说明 | 必要性 | 原因 |
|------|------|--------|------|
| auth_group | Django认证组 | ✗ 非必需 | 项目使用自定义权限系统 |
| auth_group_permissions | 组权限关联 | ✗ 非必需 | 项目使用自定义权限系统 |
| django_admin_log | Django管理后台日志 | ✗ 非必需 | 项目使用自定义日志表 |
| sys_user_groups | 用户组关联 | ✗ 非必需 | 项目未使用组功能 |
| sys_user_user_permissions | 用户权限关联 | ✗ 非必需 | 项目使用JSON字段存储权限 |

---

## 九、表关系图

```
sys_user (用户)
    ├──> biz_unit (计量单位) [created_by]
    ├──> biz_category (商品分类) [created_by]
    ├──> biz_purchase_order (采购单) [created_by]
    ├──> biz_sale_order (销售单) [created_by]
    ├──> biz_inventory_log (库存流水) [created_by]
    ├──> biz_stock_in (入库单) [created_by]
    ├──> biz_stock_out (出库单) [created_by]
    ├──> biz_stock_adjust (调整单) [created_by]
    ├──> biz_stock_transfer (调拨单) [created_by]
    ├──> biz_payment (收付款) [created_by]
    └──> sys_log (操作日志) [user]

biz_category (商品分类)
    └──> biz_goods (商品) [category]

biz_unit (计量单位)
    └──> biz_goods (商品) [unit]

biz_supplier (供应商)
    └──> biz_purchase_order (采购单) [supplier]

biz_customer (客户)
    └──> biz_sale_order (销售单) [customer]

biz_warehouse (仓库)
    ├──> biz_inventory (库存) [warehouse]
    ├──> biz_purchase_order (采购单) [warehouse]
    ├──> biz_sale_order (销售单) [warehouse]
    ├──> biz_stock_in (入库单) [warehouse]
    ├──> biz_stock_out (出库单) [warehouse]
    ├──> biz_stock_adjust (调整单) [warehouse]
    └──> biz_stock_transfer (调拨单) [from/to_warehouse]

biz_goods (商品)
    ├──> biz_purchase_item (采购明细) [goods]
    ├──> biz_sale_item (销售明细) [goods]
    ├──> biz_inventory (库存) [goods]
    ├──> biz_inventory_log (库存流水) [goods]
    ├──> biz_stock_adjust_item (调整明细) [goods]
    └──> biz_stock_transfer_item (调拨明细) [goods]
```

---

## 十、首次运行必需表清单

### 核心必需表（必须存在）

| 序号 | 表名 | 说明 |
|------|------|------|
| 1 | sys_user | 用户登录和权限管理 |
| 2 | sys_role | 角色管理 |
| 3 | sys_log | 操作日志 |
| 4 | biz_unit | 商品计量单位 |
| 5 | biz_category | 商品分类 |
| 6 | biz_warehouse | 仓库管理 |
| 7 | biz_supplier | 供应商管理 |
| 8 | biz_customer | 客户管理 |
| 9 | biz_goods | 商品信息 |
| 10 | biz_inventory | 库存数据 |
| 11 | biz_inventory_log | 库存流水 |
| 12 | biz_purchase_order | 采购单 |
| 13 | biz_purchase_item | 采购明细 |
| 14 | biz_sale_order | 销售单 |
| 15 | biz_sale_item | 销售明细 |
| 16 | biz_stock_in | 入库单 |
| 17 | biz_stock_out | 出库单 |
| 18 | biz_stock_adjust | 调整单 |
| 19 | biz_stock_adjust_item | 调整明细 |
| 20 | biz_stock_transfer | 调拨单 |
| 21 | biz_stock_transfer_item | 调拨明细 |
| 22 | biz_payment | 收付款 |
| 23 | biz_payment_record | 付款明细 |
| 24 | django_migrations | Django迁移记录 |
| 25 | django_session | Session存储 |
| 26 | django_content_type | 内容类型 |
| 27 | auth_permission | Django权限 |

### 可删除的非必需表

| 序号 | 表名 | 删除原因 |
|------|------|----------|
| 1 | auth_group | 项目使用自定义权限系统 |
| 2 | auth_group_permissions | 项目使用自定义权限系统 |
| 3 | django_admin_log | 项目使用自定义日志表 |
| 4 | sys_user_groups | 项目未使用用户组功能 |
| 5 | sys_user_user_permissions | 项目使用JSON字段存储权限 |

---

*文档生成时间: 2026-03-06*
*数据库类型: SQLite*
*Django版本: 5.x*
