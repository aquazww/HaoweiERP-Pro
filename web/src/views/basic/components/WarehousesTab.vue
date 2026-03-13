<template>
  <div class="warehouses-tab">
    <div class="tab-toolbar">
      <div class="toolbar-left">
        <el-input
          v-model="localSearch"
          placeholder="搜索仓库"
          style="width: 200px"
          clearable
          @input="$emit('search', localSearch)"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>
      <div class="toolbar-right">
        <el-button type="primary" :icon="Plus" @click="$emit('add')">新增仓库</el-button>
      </div>
    </div>
    
    <el-table
      :data="filteredWarehouseList"
      v-loading="warehouseLoading"
      border
      stripe
      highlight-current-row
      @row-click="(row) => $emit('click', row)"
    >
      <el-table-column prop="name" label="仓库名称" min-width="150" />
      <el-table-column prop="address" label="地址" min-width="200" />
      <el-table-column prop="contact" label="联系人" width="120" />
      <el-table-column prop="phone" label="联系电话" width="140" />
      <el-table-column label="状态" width="100" align="center">
        <template #default="{ row }">
          <el-switch
            :model-value="row.is_active"
            :before-change="() => handleBeforeChange(row)"
            :loading="warehouseToggleLoading === row.id"
          />
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150" align="center">
        <template #default="{ row }">
          <el-button type="primary" link size="small" @click.stop="$emit('edit', row)">编辑</el-button>
          <el-button type="danger" link size="small" @click.stop="$emit('delete', row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <el-dialog
      :model-value="warehouseDialogVisible"
      :title="warehouseDialogTitle"
      width="500px"
      destroy-on-close
      @close="$emit('dialog-close')"
    >
      <el-form
        ref="formRef"
        :model="warehouseForm"
        :rules="warehouseRules"
        label-width="80px"
      >
        <el-form-item label="仓库名称" prop="name">
          <el-input v-model="warehouseForm.name" placeholder="请输入仓库名称" />
        </el-form-item>
        <el-form-item label="地址" prop="address">
          <el-input v-model="warehouseForm.address" placeholder="请输入地址" />
        </el-form-item>
        <el-form-item label="联系人" prop="contact">
          <el-input v-model="warehouseForm.contact" placeholder="请输入联系人" />
        </el-form-item>
        <el-form-item label="联系电话" prop="phone">
          <el-input v-model="warehouseForm.phone" placeholder="请输入联系电话" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="$emit('dialog-close')">取消</el-button>
        <el-button type="primary" @click="$emit('submit')" :loading="warehouseSubmitLoading">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ElMessageBox } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'

const props = defineProps({
  warehouseList: { type: Array, default: () => [] },
  warehouseLoading: { type: Boolean, default: false },
  warehouseSearch: { type: String, default: '' },
  selectedWarehouse: { type: Object, default: null },
  warehouseDialogVisible: { type: Boolean, default: false },
  warehouseDialogTitle: { type: String, default: '' },
  warehouseForm: { type: Object, default: () => ({}) },
  warehouseRules: { type: Object, default: () => ({}) },
  warehouseSubmitLoading: { type: Boolean, default: false },
  warehouseToggleLoading: { type: [Number, null], default: null },
  filteredWarehouseList: { type: Array, default: () => [] }
})

const emit = defineEmits(['search', 'add', 'edit', 'delete', 'toggle-status', 'click', 'submit', 'dialog-close'])

const localSearch = ref(props.warehouseSearch)
const formRef = ref(null)

watch(() => props.warehouseSearch, (val) => {
  localSearch.value = val
})

const handleBeforeChange = async (row) => {
  const newStatus = !row.is_active
  try {
    await ElMessageBox.confirm(
      `确定要${newStatus ? '启用' : '停用'}仓库「${row.name}」吗？`,
      '提示',
      { type: 'warning' }
    )
    row.is_active = newStatus
    emit('toggle-status', row)
    return true
  } catch {
    return false
  }
}

defineExpose({ formRef })
</script>

<style scoped>
.warehouses-tab {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.tab-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
</style>
