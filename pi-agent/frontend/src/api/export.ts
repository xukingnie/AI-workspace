import request from './request'

/**
 * 导出 Excel：直接触发浏览器下载
 */
export const exportExcel = (startDate?: string, endDate?: string) => {
  const params: Record<string, string> = {}
  if (startDate) params.start_date = startDate
  if (endDate) params.end_date = endDate

  return request.get('/export/excel', {
    params,
    responseType: 'blob',
  }).then((res) => {
    downloadBlob(res.data, '账单明细.xlsx')
  })
}

/**
 * 导出 PDF：直接触发浏览器下载
 */
export const exportPDF = (startDate?: string, endDate?: string) => {
  const params: Record<string, string> = {}
  if (startDate) params.start_date = startDate
  if (endDate) params.end_date = endDate

  return request.get('/export/pdf', {
    params,
    responseType: 'blob',
  }).then((res) => {
    downloadBlob(res.data, '账单明细.pdf')
  })
}

/** 触发浏览器下载 Blob */
function downloadBlob(data: Blob, filename: string) {
  const url = window.URL.createObjectURL(data)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  window.URL.revokeObjectURL(url)
}
