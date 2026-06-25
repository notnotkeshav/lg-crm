import { ref, computed } from 'vue'
import { createResource } from 'frappe-ui'

export function useContract(name) {
  const contract = ref({
    doctype: 'CRM Contract',
    name: name,
    customer: '',
    customer_name: '',
    date: new Date().toISOString().split('T')[0],
    company: '',
    customer_hc: '',
    items: []
  })

  const resource = createResource({
    url: 'frappe.client.get',
    params: {
      doctype: 'CRM Contract',
      name: name
    },
    auto: name !== 'new',
    transform(data) {
      if (data) {
        contract.value = { ...contract.value, ...data }
      }
      return data
    }
  })

  const saveResource = createResource({
    url: 'frappe.client.save',
    onSuccess(data) {
      if (data) {
        contract.value.name = data.name
      }
    }
  })

  const deleteResource = createResource({
    url: 'frappe.client.delete',
    params: {
      doctype: 'CRM Contract',
      name: name
    }
  })

  async function save() {
    return await saveResource.submit({
      doc: contract.value
    })
  }

  async function remove() {
    return await deleteResource.submit()
  }

  const isNew = computed(() => !contract.value.name || contract.value.name === 'new')

  const loading = computed(() => resource.loading || saveResource.loading || deleteResource.loading)

  return {
    contract,
    isNew,
    loading,
    save,
    remove,
    reload: resource.reload
  }
}

export function useContractList() {
  const filters = ref({})
  const orderBy = ref('modified desc')
  const limit = ref(20)
  const offset = ref(0)

  const resource = createResource({
    url: 'frappe.client.get_list',
    params: computed(() => ({
      doctype: 'CRM Contract',
      fields: ['name', 'customer', 'customer_name', 'date', 'company'],
      filters: filters.value,
      order_by: orderBy.value,
      limit: limit.value,
      start: offset.value
    })),
    auto: true
  })

  function setFilters(newFilters) {
    filters.value = newFilters
    offset.value = 0
    resource.reload()
  }

  function loadMore() {
    offset.value += limit.value
    resource.reload()
  }

  return {
    contracts: computed(() => resource.data || []),
    loading: computed(() => resource.loading),
    filters,
    orderBy,
    setFilters,
    loadMore,
    reload: resource.reload
  }
} 