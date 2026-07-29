import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  ChevronLeft,
  ChevronRight,
  Info,
  Download,
  X,
  SkipForward,
} from 'lucide-react'
import { useAppStore } from '../store'
import { downloadCSV } from '../utils/csvParser'

export default function AnnotationPage() {
  const navigate = useNavigate()
  const {
    rows,
    allColumns,
    guideColumns,
    mainGuideColumn,
    annotationColumns,
    columnInputConfigs,
    guide,
    currentRowIndex,
    fileName,
    updateRowField,
    goToRow,
    nextRow,
    prevRow,
    saveToLocalStorage,
    loadFromLocalStorage,
  } = useAppStore()

  const [infoModalTable, setInfoModalTable] = useState<number | null>(null)
  const [jumpValue, setJumpValue] = useState('')

  useEffect(() => {
    loadFromLocalStorage()
  }, [loadFromLocalStorage])

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setInfoModalTable(null)
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [])

  const usableIndices = useMemo(
    () =>
      rows.reduce<number[]>((acc, row, idx) => {
        const val = mainGuideColumn ? row[mainGuideColumn] : undefined
        if (!mainGuideColumn || (typeof val === 'string' && val.trim() !== '')) {
          acc.push(idx)
        }
        return acc
      }, []),
    [rows, mainGuideColumn],
  )

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

  const currentRow = rows[currentRowIndex]

  const positionInUsable = usableIndices.indexOf(currentRowIndex)
  const usableTotal = usableIndices.length
  const isLastUsable = positionInUsable === -1 || positionInUsable === usableTotal - 1
  const progressPct =
    usableTotal > 0 ? Math.round(((positionInUsable + 1) / usableTotal) * 100) : 0

  const handleSaveAndNext = () => {
    saveToLocalStorage()
    if (!isLastUsable) {
      nextRow()
    } else {
      navigate('/review')
    }
  }

  const handleSkip = () => {
    if (!isLastUsable) {
      nextRow()
    } else {
      navigate('/review')
    }
  }

  const handleJump = () => {
    const pos = parseInt(jumpValue, 10) - 1
    if (!isNaN(pos) && pos >= 0 && pos < usableIndices.length) {
      goToRow(usableIndices[pos])
    }
    setJumpValue('')
  }

  const handleExport = () => {
    downloadCSV(rows, allColumns, fileName ? `annotated_${fileName}` : 'annotated.csv')
  }

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      {/* Header */}
      <div className="bg-white border-b border-slate-200 px-6 py-3 flex items-center gap-4 sticky top-0 z-10">
        <span className="text-sm font-medium text-slate-600">
          Row {positionInUsable + 1} of {usableTotal}
        </span>
        <div className="flex-1 h-2 bg-slate-100 rounded-full overflow-hidden max-w-xs">
          <div
            className="h-full bg-indigo-500 transition-all"
            style={{ width: `${progressPct}%` }}
          />
        </div>
        <span className="text-xs text-slate-400">{progressPct}%</span>

        <div className="flex items-center gap-2 ml-auto">
          <button
            onClick={prevRow}
            disabled={positionInUsable <= 0}
            className="p-2 rounded-lg hover:bg-slate-100 disabled:opacity-40"
            title="Previous"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          <input
            value={jumpValue}
            onChange={(e) => setJumpValue(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleJump()}
            placeholder="Go to #"
            className="w-20 border border-slate-300 rounded-md px-2 py-1 text-sm"
          />
          <button
            onClick={handleExport}
            className="flex items-center gap-1 px-3 py-1.5 text-sm bg-slate-100 hover:bg-slate-200 rounded-lg text-slate-700"
          >
            <Download className="w-4 h-4" /> Export
          </button>
        </div>
      </div>

      <div className="flex-1 max-w-4xl w-full mx-auto p-6">
        {/* Guide Section */}
        <div className="bg-white border border-slate-200 rounded-xl p-5 mb-6">
          <div className="flex gap-4 mb-3 flex-wrap">
            {guideColumns
              .filter((c) => c !== mainGuideColumn)
              .map((col) => (
                <div key={col} className="text-xs text-slate-500">
                  <span className="font-semibold text-slate-600">{col}:</span>{' '}
                  <span>{currentRow[col]}</span>
                </div>
              ))}
          </div>
          {mainGuideColumn && (
            <div className="bg-indigo-50 border border-indigo-100 rounded-lg p-4">
              <div className="text-xs font-semibold text-indigo-600 mb-1 uppercase tracking-wide">
                {mainGuideColumn}
              </div>
              <div className="text-slate-800 text-base leading-relaxed whitespace-pre-wrap">
                {currentRow[mainGuideColumn]}
              </div>
            </div>
          )}
        </div>

        {/* Annotation Fields */}
        <div className="bg-white border border-slate-200 rounded-xl p-5 mb-6 space-y-4">
          {annotationColumns.map((col) => {
            const config = columnInputConfigs.find((c) => c.column === col)
            const inputType = config?.inputType ?? 'text'

            let options: string[] = []
            if (inputType === 'dropdown') {
              if (config?.customOptions && config.customOptions.length > 0) {
                options = config.customOptions
              } else if (
                guide &&
                config?.guideTableIndex !== undefined &&
                guide.tables[config.guideTableIndex]
              ) {
                const table = guide.tables[config.guideTableIndex]
                const colIdx = config.optionColumnIndex ?? 0
                options = table.rows.map((r) => r[colIdx]).filter(Boolean)
              }
            }

            return (
              <div key={col} className="flex items-start gap-3">
                <label className="w-40 pt-2 text-sm font-medium text-slate-700 flex-shrink-0">
                  {col}
                </label>
                <div className="flex-1 flex items-center gap-2">
                  {inputType === 'dropdown' ? (
                    <select
                      value={currentRow[col] ?? ''}
                      onChange={(e) => updateRowField(currentRowIndex, col, e.target.value)}
                      className="flex-1 border border-slate-300 rounded-lg px-3 py-2 text-sm"
                    >
                      <option value="">-- Select --</option>
                      {options.map((opt, i) => (
                        <option key={i} value={opt}>
                          {opt}
                        </option>
                      ))}
                    </select>
                  ) : inputType === 'number' ? (
                    <input
                      type="number"
                      value={currentRow[col] ?? ''}
                      onChange={(e) => updateRowField(currentRowIndex, col, e.target.value)}
                      className="flex-1 border border-slate-300 rounded-lg px-3 py-2 text-sm"
                    />
                  ) : (
                    <textarea
                      value={currentRow[col] ?? ''}
                      onChange={(e) => updateRowField(currentRowIndex, col, e.target.value)}
                      rows={2}
                      className="flex-1 border border-slate-300 rounded-lg px-3 py-2 text-sm resize-none"
                    />
                  )}

                  {inputType === 'dropdown' &&
                    guide &&
                    config?.guideTableIndex !== undefined && (
                      <button
                        onClick={() => setInfoModalTable(config.guideTableIndex!)}
                        className="p-2 rounded-full hover:bg-slate-100 text-slate-400 hover:text-indigo-600"
                        title="View guide table"
                      >
                        <Info className="w-4 h-4" />
                      </button>
                    )}
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Footer */}
      <div className="bg-white border-t border-slate-200 px-6 py-4 flex items-center justify-between sticky bottom-0">
        <span className="text-xs text-slate-400">
          Shortcuts: Ctrl+Enter Save & Next &middot; Esc Close modal
        </span>
        <div className="flex gap-2">
          <button
            onClick={handleSkip}
            className="flex items-center gap-1 px-4 py-2 rounded-lg text-slate-600 hover:bg-slate-100 text-sm font-medium"
          >
            <SkipForward className="w-4 h-4" /> Skip
          </button>
          <button
            onClick={handleSaveAndNext}
            className="flex items-center gap-1 px-6 py-2 rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 text-sm font-medium"
          >
            Save <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Guide Info Modal */}
      {infoModalTable !== null && guide && guide.tables[infoModalTable] && (
        <div
          className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4"
          onClick={() => setInfoModalTable(null)}
        >
          <div
            className="bg-white rounded-xl max-w-2xl w-full max-h-[80vh] overflow-auto p-6"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-slate-800">
                {guide.tables[infoModalTable].title}
              </h3>
              <button
                onClick={() => setInfoModalTable(null)}
                className="p-1 rounded-full hover:bg-slate-100"
              >
                <X className="w-5 h-5 text-slate-500" />
              </button>
            </div>
            <table className="w-full text-sm border-collapse">
              <thead>
                <tr className="border-b border-slate-200">
                  {guide.tables[infoModalTable].headers.map((h, i) => (
                    <th key={i} className="text-left py-2 px-3 font-semibold text-slate-600">
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {guide.tables[infoModalTable].rows.map((row, ri) => (
                  <tr key={ri} className="border-b border-slate-100">
                    {row.map((cell, ci) => (
                      <td key={ci} className="py-2 px-3 text-slate-700">
                        {cell}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
