<template>
  <LayoutHeader>
    <template #left-header>
      <ViewBreadcrumbs v-model="viewControls" routeName="Quotations" />
    </template>
    <template #right-header>
      <CustomActions
        v-if="quotationsListView?.customListActions"
        :actions="quotationsListView.customListActions"
      />
      <Button
        variant="solid"
        :label="__('Create')"
        @click="showQuotationModal = true"
      >
        <template #prefix><FeatherIcon name="plus" class="h-4" /></template>
      </Button>
    </template>
  </LayoutHeader>
  <ViewControls
    ref="viewControls"
    v-model="quotations"
    v-model:loadMore="loadMore"
    v-model:resizeColumn="triggerResize"
    v-model:updatedPageCount="updatedPageCount"
    doctype="CRM Quotation"
    :options="{
      allowedViews: ['list'],
    }"
  />
  <QuotationsListView
    ref="quotationsListView"
    v-if="quotations.data && rows.length"
    v-model="quotations.data.page_length_count"
    v-model:list="quotations"
    :rows="rows"
    :columns="quotations.data.columns"
    :options="{
      showTooltip: false,
      resizeColumn: true,
      rowCount: quotations.data.row_count,
      totalCount: quotations.data.total_count,
    }"
    @loadMore="() => loadMore++"
    @columnWidthUpdated="() => triggerResize++"
    @updatePageCount="(count) => (updatedPageCount = count)"
    @applyFilter="(data) => viewControls.applyFilter(data)"
    @applyLikeFilter="(data) => viewControls.applyLikeFilter(data)"
    @likeDoc="(data) => viewControls.likeDoc(data)"
  />
  <div v-else-if="quotations.data" class="flex h-full items-center justify-center">
    <div class="flex flex-col items-center gap-3 text-xl font-medium text-gray-500">
      <QuotationsIcon class="h-10 w-10" />
      <span>{{ __('No {0} Found', [__('Quotations')]) }}</span>
      <Button :label="__('Create')" @click="showQuotationModal = true">
        <template #prefix><FeatherIcon name="plus" class="h-4" /></template>
      </Button>
    </div>
  </div>
  <QuotationModal
    v-if="showQuotationModal"
    v-model="showQuotationModal"
    v-model:quickEntry="showQuickEntryModal"
    :defaults="defaults"
  />
  <QuickEntryModal
    v-if="showQuickEntryModal"
    v-model="showQuickEntryModal"
    doctype="CRM Quotation"
  />
</template>

<script setup>
import ViewBreadcrumbs from '@/components/ViewBreadcrumbs.vue'
import CustomActions from '@/components/CustomActions.vue'
import QuotationsIcon from '@/components/Icons/QuotationsIcon.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import QuotationsListView from '@/components/ListViews/QuotationsListView.vue'
import QuotationModal from '@/components/Modals/QuotationModal.vue'
import QuickEntryModal from '@/components/Modals/QuickEntryModal.vue'
import ViewControls from '@/components/ViewControls.vue'
import { FeatherIcon } from 'frappe-ui'
import { ref, reactive, computed } from 'vue'
import { useRoute } from 'vue-router'
import { dateFormat, dateTooltipFormat, timeAgo } from '@/utils'

const route = useRoute()

const quotationsListView = ref(null)
const showQuotationModal = ref(false)
const showQuickEntryModal = ref(false)

const defaults = reactive({})

// quotations data is loaded in the ViewControls component
const quotations = ref({
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
  if (!quotations.value?.data?.data) return []
  return parseRows(quotations.value?.data.data)
})

function parseRows(rows = []) {
  return rows.map((quotation) => {
    let _rows = {}
    if (quotations.value?.data?.rows) {
      quotations.value.data.rows.forEach((row) => {
        _rows[row] = quotation[row]

        if (row == 'customer') {
          _rows[row] = {
            label: quotation.customer_name,
            logo: quotation.customer_image,
          }
        } else if (row == 'date') {
          _rows[row] = {
            label: dateFormat(quotation.date, dateTooltipFormat),
            timeAgo: timeAgo(quotation.date),
          }
        } else if (row == 'modified' || row == 'creation') {
          _rows[row] = {
            label: dateFormat(quotation[row], dateTooltipFormat),
            timeAgo: timeAgo(quotation[row]),
          }
        }
      })
    }
    return _rows
  })
}
</script>

