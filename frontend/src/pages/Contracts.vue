<template>
  <LayoutHeader>
    <template #left-header>
      <ViewBreadcrumbs v-model="viewControls" routeName="Contracts" />
    </template>
    <template #right-header>
      <CustomActions
        v-if="contractsListView?.customListActions"
        :actions="contractsListView.customListActions"
      />
      <Button
        variant="solid"
        :label="__('Create')"
        @click="showContractModal = true"
      >
        <template #prefix><FeatherIcon name="plus" class="h-4" /></template>
      </Button>
    </template>
  </LayoutHeader>
  <ViewControls
    ref="viewControls"
    v-model="contracts"
    v-model:loadMore="loadMore"
    v-model:resizeColumn="triggerResize"
    v-model:updatedPageCount="updatedPageCount"
    doctype="CRM Contract"
    :options="{
      allowedViews: ['list'],
    }"
  />
  <ContractsListView
    ref="contractsListView"
    v-if="contracts.data && rows.length"
    v-model="contracts.data.page_length_count"
    v-model:list="contracts"
    :rows="rows"
    :columns="contracts.data.columns"
    :options="{
      showTooltip: false,
      resizeColumn: true,
      rowCount: contracts.data.row_count,
      totalCount: contracts.data.total_count,
    }"
    @loadMore="() => loadMore++"
    @columnWidthUpdated="() => triggerResize++"
    @updatePageCount="(count) => (updatedPageCount = count)"
    @applyFilter="(data) => viewControls.applyFilter(data)"
    @applyLikeFilter="(data) => viewControls.applyLikeFilter(data)"
    @likeDoc="(data) => viewControls.likeDoc(data)"
  />
  <div v-else-if="contracts.data" class="flex h-full items-center justify-center">
    <div class="flex flex-col items-center gap-3 text-xl font-medium text-gray-500">
      <ContractsIcon class="h-10 w-10" />
      <span>{{ __('No {0} Found', [__('Contracts')]) }}</span>
      <Button :label="__('Create')" @click="showContractModal = true">
        <template #prefix><FeatherIcon name="plus" class="h-4" /></template>
      </Button>
    </div>
  </div>
  <ContractModal
    v-if="showContractModal"
    v-model="showContractModal"
    v-model:quickEntry="showQuickEntryModal"
    :defaults="defaults"
  />
  <QuickEntryModal
    v-if="showQuickEntryModal"
    v-model="showQuickEntryModal"
    doctype="CRM Contract"
  />
</template>

<script setup>
import ViewBreadcrumbs from '@/components/ViewBreadcrumbs.vue'
import CustomActions from '@/components/CustomActions.vue'
import ContractsIcon from '@/components/Icons/ContractsIcon.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import ContractsListView from '@/components/ListViews/ContractsListView.vue'
import ContractModal from '@/components/Contract/ContractModal.vue'
import QuickEntryModal from '@/components/Modals/QuickEntryModal.vue'
import ViewControls from '@/components/ViewControls.vue'
import { FeatherIcon } from 'frappe-ui'
import { ref, reactive, computed } from 'vue'
import { useRoute } from 'vue-router'
import { dateFormat, dateTooltipFormat, timeAgo } from '@/utils'

const route = useRoute()

const contractsListView = ref(null)
const showContractModal = ref(false)
const showQuickEntryModal = ref(false)

const defaults = reactive({})

// contracts data is loaded in the ViewControls component
const contracts = ref({
  data: {
    data: [],
    rows: [],
    columns: [],
    page_length_count: 0,
    row_count: 0,
    total_count: 0
  }
})
const loadMore = ref(1)
const triggerResize = ref(1)
const updatedPageCount = ref(20)
const viewControls = ref(null)

// Rows
const rows = computed(() => {
  if (!contracts.value?.data?.data) return []
  return parseRows(contracts.value?.data.data)
})

function parseRows(rows = []) {
  return rows.map((contract) => {
    let _rows = {}
    if (contracts.value?.data?.rows) {
      contracts.value.data.rows.forEach((row) => {
        _rows[row] = contract[row]

        if (row == 'customer') {
          _rows[row] = {
            label: contract.customer_name,
            logo: contract.customer_image,
          }
        } else if (row == 'date') {
          _rows[row] = {
            label: dateFormat(contract.date, dateTooltipFormat),
            timeAgo: timeAgo(contract.date),
          }
        } else if (row == 'modified' || row == 'creation') {
          _rows[row] = {
            label: dateFormat(contract[row], dateTooltipFormat),
            timeAgo: timeAgo(contract[row]),
          }
        }
      })
    }
    return _rows
  })
}
</script> 