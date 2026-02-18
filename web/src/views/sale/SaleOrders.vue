<template>
  <div class="sale-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>销售订单</span>
          <el-button type="primary" @click="handleAdd">新增销售单</el-button>
        </div>
      </template>
      
      <el-table :data="orderList" style="width: 100%" v-loading="loading">
        <el-table-column prop="order_no" label="销售单号" width="150" />
        <el-table-column prop="customer_name" label="客户" width="150" />
        <el-table-column prop="warehouse_name" label="仓库" width="120" />
        <el-table-column prop="total_amount" label="总金额" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleView(row)">查看</el-button>
            <el-button type="warning" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="success" link @click="handleStockOut(row)">出库</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增/编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑销售单' : '新增销售单'"
      width="900px"
      destroy-on-close
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="客户" prop="customer">
              <el-select v-model="form.customer" placeholder="请选择客户" style="width: 100%">
                <el-option 
                  v-for="item in customerList" 
                  :key="item.id" 
                  :label="item.name" 
                  :value="item.id" 
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="仓库" prop="warehouse">
              <el-select v-model="form.warehouse" placeholder="请选择仓库" style="width: 100%">
                <el-option 
                  v-for="item in warehouseList" 
                  :key="item.id" 
                  :label="item.name" 
                  :value="item.id" 
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="销售日期" prop="order_date">
          <el-date-picker
            v-model="form.order_date"
            type="date"
            placeholder="选择日期"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="3" placeholder="请输入备注" />
        </el-form-item>

        <el-divider content-position="left">销售明细</el-divider>
        
        <el-table :data="form.items" border style="width: 100%; margin-bottom: 20px;">
          <el-table-column prop="goods" label="商品" min-width="200">
            <template #default="{ row, $index }">
              <el-select v-model="row.goods" placeholder="选择商品" style="width: 100%">
                <el-option 
                  v-for="item in goodsList" 
                  :key="item.id" 
                  :label="item.name" 
                  :value="item.id" 
                  @change="handleGoodsChange(row)"
                />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column prop="quantity" label="数量" width="120">
            <template #default="{ row }">
              <el-input-number v-model="row.quantity" :min="0" :precision="2" style="width: 100%" />
            </template>
          </el-table-column>
          <el-table-column prop="price" label="单价" width="120">
            <template #default="{ row }">
              <el-input-number v-model="row.price" :min="0" :precision="2" style="width: 100%" />
            </template>
          </el-table-column>
          <el-table-column prop="amount" label="金额" width="120">
            <template #default="{ row }">
              <span>{{ (row.quantity * row.price).toFixed(2) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100">
            <template #default="{ $index }">
              <el-button type="danger" link @click="removeItem($index)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-button type="primary" plain @click="addItem">+ 添加明细</el-button>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitLoading">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  getSaleOrders, createSaleOrder, 
  updateSaleOrder, deleteSaleOrder,
  confirmSaleOrder
} from '../../api/sale'
import { getCustomers, getWarehouses, getGoods } from '../../api/basic'
import { createStockOut } from '../../api/inventory'

const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)
const orderList = ref([])
const customerList = ref([])
const warehouseList = ref([])
const goodsList = ref([])

const form = ref({
  customer: '',
  warehouse: '',
  order_date: new Date(),
  remark: '',
  items: []
})

const rules = {
  customer: [{ required: true, message: '请选择客户', trigger: 'change' }],
  warehouse: [{ required: true, message: '请选择仓库', trigger: 'change' }],
  order_date: [{ required: true, message: '请选择日期', trigger: 'change' }]
}

const getStatusType = (status) => {
  const typeMap = {
    'pending': 'warning',
    'partial': 'info',
    'completed': 'success',
    'cancelled': 'danger'
  }
  return typeMap[status] || ''
}

const getStatusText = (status) => {
  const textMap = {
    'pending': '待出库',
    'partial': '部分出库',
    'completed': '已出库',
    'cancelled': '已取消'
  }
  return textMap[status] || status
}

const totalAmount = computed(() => {
  return form.value.items.reduce((sum, item) => {
    return sum + (item.quantity * item.price || 0)
  }, 0).toFixed(2)
})

const loadOrders = async () => {
  loading.value = true
  try {
    const res = await getSaleOrders()
    orderList.value = res.data.items || []
  } catch (error) {
    ElMessage.error('加载销售订单失败')
  } finally {
    loading.value = false
  }
}

const loadOptions = async () => {
  try {
    const [customersRes, warehousesRes, goodsRes] = await Promise.all([
      getCustomers(),
      getWarehouses(),
      getGoods()
    ])
    customerList.value = customersRes.data.items || []
    warehouseList.value = warehousesRes.data.items || []
    goodsList.value = goodsRes.data.items || []
  } catch (error) {
    ElMessage.error('加载选项数据失败')
  }
}

const handleAdd = () => {
  isEdit.value = false
  form.value = {
    customer: '',
    warehouse: '',
    order_date: new Date(),
    remark: '',
    items: []
  }
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  form.value = {
    id: row.id,
    customer: row.customer,
    warehouse: row.warehouse,
    order_date: row.order_date,
    remark: row.remark,
    items: row.items ? [...row.items] : []
  }
  dialogVisible.value = true
}

const handleView = (row) => {
  ElMessage.info('查看销售单功能开发中')
}

const handleStockOut = async (row) => {
  if (row.status === 'completed') {
    ElMessage.warning('该销售单已全部出库')
    return
  }

  try {
    await ElMessageBox.confirm('确定要出库此销售单吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    // 1. 创建出库单
    const stockOutData = {
      sale_order: row.id,
      warehouse: row.warehouse,
      total_amount: row.total_amount,
      remark: `销售单 ${row.order_no} 出库`
    }
    
    await createStockOut(stockOutData)
    
    // 2. 确认出库
    await confirmSaleOrder(row.id)
    
    ElMessage.success('出库成功')
    loadOrders()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '出库失败')
    }
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该销售单吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deleteSaleOrder(row.id)
    ElMessage.success('删除成功')
    loadOrders()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const addItem = () => {
  form.value.items.push({
    goods: '',
    quantity: 1,
    price: 0,
    remark: ''
  })
}

const removeItem = (index) => {
  form.value.items.splice(index, 1)
}

const handleGoodsChange = (row) => {
  const goods = goodsList.value.find(g => g.id === row.goods)
  if (goods) {
    row.price = goods.sale_price
  }
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    submitLoading.value = true
    
    const data = {
      ...form.value,
      total_amount: parseFloat(totalAmount.value)
    }
    
    if (isEdit.value) {
      await updateSaleOrder(form.value.id, data)
      ElMessage.success('更新成功')
    } else {
      await createSaleOrder(data)
      ElMessage.success('创建成功')
    }
    
    dialogVisible.value = false
    loadOrders()
  } catch (error) {
    if (error !== false) {
      ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
    }
  } finally {
    submitLoading.value = false
  }
}

onMounted(() => {
  loadOrders()
  loadOptions()
})
</script>

<style scoped>
.sale-page {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
