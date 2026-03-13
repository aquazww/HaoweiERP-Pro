<template>
  <el-dialog
    :title="dialogTitle"
    v-model="dialogVisible"
    width="80%"
    :before-close="handleClose"
  >
    <div v-if="currentStep === 'config'">
      <print-config
        :fields="fields"
        :printSettings="printSettings"
        @confirm="handleConfigConfirm"
        @cancel="handleConfigCancel"
      />
    </div>
    <div v-else-if="currentStep === 'preview'">
      <print-preview
        :printSettings="printSettings"
        @close="handlePreviewClose"
      >
        <div class="print-data">
          <h2 style="text-align: center; margin-bottom: 20px;">{{ printSettings.title }}</h2>
          <div v-if="data && data.length > 0">
            <table>
              <thead>
                <tr>
                  <th v-for="field in visibleFields" :key="field.key">{{ field.label }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(item, index) in data" :key="index">
                  <td v-for="field in visibleFields" :key="field.key">
                    {{ item[field.key] || '' }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-else>
            <p style="text-align: center; color: #909399;">暂无数据</p>
          </div>
        </div>
      </print-preview>
    </div>
  </el-dialog>
</template>

<script>
import PrintConfig from './PrintConfig.vue';
import PrintPreview from './PrintPreview.vue';

export default {
  name: 'PrintDialog',
  components: {
    PrintConfig,
    PrintPreview
  },
  props: {
    modelValue: {
      type: Boolean,
      default: false
    },
    fields: {
      type: Array,
      required: true
    },
    data: {
      type: Array,
      default: () => []
    },
    title: {
      type: String,
      default: '打印'
    }
  },
  emits: ['update:modelValue'],
  data() {
    return {
      dialogVisible: this.modelValue,
      currentStep: 'config',
      printSettings: {
        paperSize: 'A4',
        orientation: 'portrait',
        margins: {
          top: 10,
          right: 10,
          bottom: 10,
          left: 10
        },
        title: '打印预览',
        fontSize: '12px',
        header: '',
        footer: '',
        showPageNumbers: true,
        showDate: true
      },
      originalFields: []
    };
  },
  computed: {
    dialogTitle() {
      return this.currentStep === 'config' ? `${this.title}配置` : `${this.title}预览`;
    },
    visibleFields() {
      return this.fields.filter(field => field.visible);
    }
  },
  watch: {
    modelValue(val) {
      this.dialogVisible = val;
      if (val) {
        // 保存原始字段配置
        this.originalFields = structuredClone(this.fields);
        this.currentStep = 'config';
      }
    },
    dialogVisible(val) {
      this.$emit('update:modelValue', val);
    }
  },
  methods: {
    handleClose() {
      // 恢复原始字段配置
      this.fields.splice(0, this.fields.length, ...this.originalFields);
      this.dialogVisible = false;
    },
    handleConfigCancel() {
      // 恢复原始字段配置
      this.fields.splice(0, this.fields.length, ...this.originalFields);
      this.dialogVisible = false;
    },
    handleConfigConfirm(config) {
      this.printSettings = config.printSettings;
      this.currentStep = 'preview';
    },
    handlePreviewClose() {
      this.currentStep = 'config';
    }
  }
};
</script>

<style scoped>
.print-data {
  width: 100%;
}

.print-data table {
  width: 100%;
  border-collapse: collapse;
}

.print-data th,
.print-data td {
  border: 1px solid #000;
  padding: 8px;
  text-align: left;
}

.print-data th {
  background-color: #f2f2f2;
  font-weight: bold;
}
</style>
