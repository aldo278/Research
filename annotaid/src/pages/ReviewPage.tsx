import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Download, ArrowLeft, Search } from 'lucide-react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from 'recharts'
import { useAppStore } from '../store'
import { downloadCSV } from '../utils/csvParser'

export default function ReviewPage() {
  const navigate = useNavigate()
  const { rows, allColumns, annotationColumns, fileName, goToRow } = useAppStore()
  const [search, setSearch] = useState('')
  const [showOnlyUnannotated, setShowOnlyUnannotated] = useState(false)

  const isRowAnnotated = (row: Record<string, string>) =>
    annotationColumns.some((col) => row[col] && row[col].trim() !== '')

  const totalAnnotated = useMemo(
    () => rows.filter(isRowAnnotated).length,
    [rows, annotationColumns],
  )
  const completionPct = rows.length > 0 ? Math.round((totalAnnotated / rows.length) * 100) : 0

  const categoryDistribution = useMemo(() => {
    const col = annotationColumns.find((c) => c.toLowerCase().includes('category'))
    if (!col) return []
    const counts: Record<string, number> = {}
    rows.forEach((r) => {
      const val = r[col] || 'Unlabeled'
      counts[val] = (counts[val] || 0) + 1
    })
    return Object.entries(counts).map(([name, value]) => ({ name, value }))
  }, [rows, annotationColumns])

  const qualityDistribution = useMemo(() => {
    const col = annotationColumns.find((c) => c.toLowerCase().includes('quality'))
    if (!col) return []
    const counts: Record<string, number> = {}
    rows.forEach((r) => {
      const val = r[col] || 'Unlabeled'
      counts[val] = (counts[val] || 0) + 1
    })
    return Object.entries(counts).map(([name, value]) => ({ name, value }))
  }, [rows, annotationColumns])

  const filteredRows = useMemo(() => {
    return rows
      .map((row, idx) => ({ row, idx }))
      .filter(({ row }) => {
        if (showOnlyUnannotated && isRowAnnotated(row)) return false
        if (search) {
          const searchLower = search.toLowerCase()
          return Object.values(row).some((v) => v?.toLowerCase().includes(searchLower))
        }
        return true
      })
  }, [rows, search, showOnlyUnannotated, annotationColumns])

  const handleExport = () => {
    downloadCSV(rows, allColumns, fileName ? `annotated_${fileName}` : 'annotated.csv')
  }

  if (rows.length === 0) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-slate-600 mb-4">No file loaded yet.</p>
          <button
            onClick={() => navigate('/')}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg"
          >
            Go to Upload
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-50 p-6">
      <div className="max-w-5xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold text-slate-800">Review & Export</h1>
          <div className="flex gap-2">
            <button
              onClick={() => navigate('/annotate')}
              className="flex items-center gap-1 px-4 py-2 rounded-lg text-slate-600 hover:bg-slate-100 text-sm"
            >
              <ArrowLeft className="w-4 h-4" /> Back to Annotation
            </button>
            <button
              onClick={handleExport}
              className="flex items-center gap-1 px-4 py-2 rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 text-sm font-medium"
            >
              <Download className="w-4 h-4" /> Export CSV
            </button>
          </div>
        </div>

        {/* Summary Stats */}
        <div className="grid grid-cols-3 gap-4 mb-6">
          <StatCard label="Total Rows" value={rows.length.toString()} />
          <StatCard label="Annotated" value={totalAnnotated.toString()} />
          <StatCard label="Completion" value={`${completionPct}%`} />
        </div>

        {/* Charts */}
        <div className="grid grid-cols-2 gap-4 mb-6">
          {categoryDistribution.length > 0 && (
            <ChartCard title="Risk Category Distribution" data={categoryDistribution} />
          )}
          {qualityDistribution.length > 0 && (
            <ChartCard title="Disclosure Quality Distribution" data={qualityDistribution} />
          )}
        </div>

        {/* Filters */}
        <div className="flex items-center gap-3 mb-4">
          <div className="flex-1 flex items-center gap-2 bg-white border border-slate-300 rounded-lg px-3 py-2">
            <Search className="w-4 h-4 text-slate-400" />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search rows..."
              className="flex-1 outline-none text-sm"
            />
          </div>
          <label className="flex items-center gap-2 text-sm text-slate-600">
            <input
              type="checkbox"
              checked={showOnlyUnannotated}
              onChange={(e) => setShowOnlyUnannotated(e.target.checked)}
              className="accent-indigo-600"
            />
            Show only unannotated
          </label>
        </div>

        {/* Table */}
        <div className="bg-white border border-slate-200 rounded-xl overflow-auto max-h-[500px]">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 sticky top-0">
              <tr>
                <th className="text-left px-3 py-2 font-semibold text-slate-600">#</th>
                {allColumns.map((col) => (
                  <th key={col} className="text-left px-3 py-2 font-semibold text-slate-600">
                    {col}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filteredRows.map(({ row, idx }) => (
                <tr
                  key={idx}
                  onClick={() => {
                    goToRow(idx)
                    navigate('/annotate')
                  }}
                  className="border-t border-slate-100 hover:bg-indigo-50 cursor-pointer"
                >
                  <td className="px-3 py-2 text-slate-400">{idx + 1}</td>
                  {allColumns.map((col) => (
                    <td key={col} className="px-3 py-2 text-slate-700 max-w-xs truncate">
                      {row[col]}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-white border border-slate-200 rounded-xl p-4">
      <div className="text-2xl font-bold text-slate-800">{value}</div>
      <div className="text-sm text-slate-500">{label}</div>
    </div>
  )
}

function ChartCard({
  title,
  data,
}: {
  title: string
  data: { name: string; value: number }[]
}) {
  return (
    <div className="bg-white border border-slate-200 rounded-xl p-4">
      <h3 className="text-sm font-semibold text-slate-700 mb-3">{title}</h3>
      <ResponsiveContainer width="100%" height={200}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" fontSize={12} />
          <YAxis fontSize={12} />
          <Tooltip />
          <Bar dataKey="value" fill="#6366f1" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
