import { useMemo, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { CheckCircle2, Upload, ArrowLeft, ArrowRight } from 'lucide-react'
import { useAppStore } from '../store'
import { parseGuideFile } from '../utils/guideParser'
import type { ColumnInputConfig, InputType } from '../types'

export default function ConfigPage() {
  const navigate = useNavigate()
  const {
    fileName,
    rows,
    allColumns,
    annotationColumns,
    guideColumns,
    mainGuideColumn,
    guide,
    setAnnotationColumns,
    setGuideColumns,
    setMainGuideColumn,
    setGuide,
    setColumnInputConfigs,
    goToFirstUsableRow,
  } = useAppStore()

  const guideFileInputRef = useRef<HTMLInputElement>(null)
  const [guideFileName, setGuideFileName] = useState<string>('')
  const [inputTypeMap, setInputTypeMap] = useState<Record<string, InputType>>({})
  const [tableMap, setTableMap] = useState<Record<string, number>>({})
  const [optionColMap, setOptionColMap] = useState<Record<string, number>>({})
  const [customOptionsMap, setCustomOptionsMap] = useState<Record<string, string>>({})
  const [optionSourceMap, setOptionSourceMap] = useState<Record<string, 'guide' | 'custom'>>({})

  const remainingForGuide = useMemo(
    () => allColumns.filter((c) => !annotationColumns.includes(c)),
    [allColumns, annotationColumns],
  )

  const toggleAnnotationColumn = (col: string) => {
    if (annotationColumns.includes(col)) {
      setAnnotationColumns(annotationColumns.filter((c) => c !== col))
      setGuideColumns(guideColumns.filter((c) => c !== col))
    } else {
      setAnnotationColumns([...annotationColumns, col])
    }
  }

  const toggleGuideColumn = (col: string) => {
    if (guideColumns.includes(col)) {
      setGuideColumns(guideColumns.filter((c) => c !== col))
      if (mainGuideColumn === col) setMainGuideColumn('')
    } else {
      setGuideColumns([...guideColumns, col])
    }
  }

  const handleGuideFileUpload = async (file: File) => {
    const text = await file.text()
    const parsed = parseGuideFile(text)
    setGuide(parsed)
    setGuideFileName(file.name)
  }

  const onGuideInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) handleGuideFileUpload(file)
  }

  const canProceed = annotationColumns.length > 0 && mainGuideColumn !== ''

  const handleStart = () => {
    const configs: ColumnInputConfig[] = annotationColumns.map((col) => {
      const useCustom = optionSourceMap[col] === 'custom' || !guide || guide.tables.length === 0
      const customOptions = useCustom
        ? (customOptionsMap[col] ?? '')
            .split(',')
            .map((v) => v.trim())
            .filter((v) => v.length > 0)
        : undefined
      return {
        column: col,
        inputType: inputTypeMap[col] ?? 'text',
        guideTableIndex: useCustom ? undefined : tableMap[col],
        optionColumnIndex: useCustom ? undefined : optionColMap[col],
        customOptions,
      }
    })
    setColumnInputConfigs(configs)
    goToFirstUsableRow()
    navigate('/annotate')
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
    <div className="min-h-screen bg-slate-50 py-10 px-4">
      <div className="max-w-3xl mx-auto">
        <div className="flex items-center gap-2 mb-8 text-green-700 bg-green-50 rounded-lg px-4 py-3">
          <CheckCircle2 className="w-5 h-5" />
          <span className="font-medium">{fileName} loaded successfully</span>
          <span className="text-green-600 text-sm ml-auto">{rows.length} rows</span>
        </div>

        {/* Section 1: Annotation Columns */}
        <Section title="Select column(s) you want to annotate">
          <ColumnGrid
            columns={allColumns}
            selected={annotationColumns}
            onToggle={toggleAnnotationColumn}
          />
        </Section>

        {/* Section 2: Guide Columns */}
        <Section title="Select column(s) you would like to use as a guide">
          <ColumnGrid
            columns={remainingForGuide}
            selected={guideColumns}
            onToggle={toggleGuideColumn}
          />
        </Section>

        {/* Section 3: Main Guide */}
        <Section title="Select the main guide">
          <select
            value={mainGuideColumn}
            onChange={(e) => setMainGuideColumn(e.target.value)}
            className="w-full border border-slate-300 rounded-lg px-3 py-2 bg-white"
          >
            <option value="">-- Select a column --</option>
            {guideColumns.map((col) => (
              <option key={col} value={col}>
                {col}
              </option>
            ))}
          </select>
        </Section>

        {/* Section 4: Upload Guide File */}
        <Section title="Upload a guide (optional)">
          <div
            onClick={() => guideFileInputRef.current?.click()}
            className="cursor-pointer border-2 border-dashed border-slate-300 rounded-xl p-6 text-center hover:border-indigo-400 bg-white"
          >
            <Upload className="w-6 h-6 mx-auto text-indigo-500 mb-2" />
            <p className="text-slate-600 text-sm">
              {guideFileName ? guideFileName : 'Click to upload a .txt guide file'}
            </p>
            <input
              ref={guideFileInputRef}
              type="file"
              accept=".txt,.md"
              className="hidden"
              onChange={onGuideInputChange}
            />
          </div>

          {guide && guide.tables.length > 0 && (
            <div className="mt-3 text-sm text-slate-500">
              Parsed {guide.tables.length} table(s): {guide.tables.map((t) => t.title).join(', ')}
            </div>
          )}
        </Section>

        {/* Per-column input type configuration */}
        {annotationColumns.length > 0 && (
          <Section title="Configure annotation input types">
            <div className="space-y-4">
              {annotationColumns.map((col) => {
                const hasGuideTables = !!guide && guide.tables.length > 0
                const source = optionSourceMap[col] ?? (hasGuideTables ? 'guide' : 'custom')

                return (
                  <div
                    key={col}
                    className="bg-white border border-slate-200 rounded-lg p-4 flex flex-wrap items-center gap-3"
                  >
                    <span className="font-medium text-slate-700 min-w-[140px]">{col}</span>
                    <select
                      value={inputTypeMap[col] ?? 'text'}
                      onChange={(e) =>
                        setInputTypeMap({ ...inputTypeMap, [col]: e.target.value as InputType })
                      }
                      className="border border-slate-300 rounded-md px-2 py-1 text-sm"
                    >
                      <option value="text">Free Text</option>
                      <option value="dropdown">Dropdown</option>
                      <option value="number">Number</option>
                    </select>

                    {inputTypeMap[col] === 'dropdown' && (
                      <>
                        {hasGuideTables && (
                          <select
                            value={source}
                            onChange={(e) =>
                              setOptionSourceMap({
                                ...optionSourceMap,
                                [col]: e.target.value as 'guide' | 'custom',
                              })
                            }
                            className="border border-slate-300 rounded-md px-2 py-1 text-sm"
                          >
                            <option value="guide">From guide table</option>
                            <option value="custom">Enter values manually</option>
                          </select>
                        )}

                        {source === 'guide' && hasGuideTables && (
                          <>
                            <select
                              value={tableMap[col] ?? ''}
                              onChange={(e) =>
                                setTableMap({ ...tableMap, [col]: Number(e.target.value) })
                              }
                              className="border border-slate-300 rounded-md px-2 py-1 text-sm"
                            >
                              <option value="">Guide table...</option>
                              {guide!.tables.map((t, i) => (
                                <option key={i} value={i}>
                                  {t.title}
                                </option>
                              ))}
                            </select>

                            {tableMap[col] !== undefined && guide!.tables[tableMap[col]] && (
                              <select
                                value={optionColMap[col] ?? 0}
                                onChange={(e) =>
                                  setOptionColMap({
                                    ...optionColMap,
                                    [col]: Number(e.target.value),
                                  })
                                }
                                className="border border-slate-300 rounded-md px-2 py-1 text-sm"
                              >
                                {guide!.tables[tableMap[col]].headers.map((h, i) => (
                                  <option key={i} value={i}>
                                    {h}
                                  </option>
                                ))}
                              </select>
                            )}
                          </>
                        )}

                        {source === 'custom' && (
                          <input
                            type="text"
                            value={customOptionsMap[col] ?? ''}
                            onChange={(e) =>
                              setCustomOptionsMap({ ...customOptionsMap, [col]: e.target.value })
                            }
                            placeholder="Enter comma-separated values, e.g. Low, Medium, High"
                            className="flex-1 min-w-[240px] border border-slate-300 rounded-md px-2 py-1 text-sm"
                          />
                        )}
                      </>
                    )}
                  </div>
                )
              })}
            </div>
          </Section>
        )}

        <div className="flex justify-between mt-8">
          <button
            onClick={() => navigate('/')}
            className="flex items-center gap-1 px-4 py-2 text-slate-600 hover:text-slate-800"
          >
            <ArrowLeft className="w-4 h-4" /> Back
          </button>
          <button
            disabled={!canProceed}
            onClick={handleStart}
            className={`flex items-center gap-1 px-6 py-2 rounded-lg font-medium ${
              canProceed
                ? 'bg-indigo-600 text-white hover:bg-indigo-700'
                : 'bg-slate-200 text-slate-400 cursor-not-allowed'
            }`}
          >
            Start Annotation <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  )
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="mb-8">
      <h2 className="text-lg font-semibold text-slate-800 mb-3">{title}</h2>
      {children}
    </div>
  )
}

function ColumnGrid({
  columns,
  selected,
  onToggle,
}: {
  columns: string[]
  selected: string[]
  onToggle: (col: string) => void
}) {
  if (columns.length === 0) {
    return <p className="text-slate-400 text-sm">No columns available.</p>
  }
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
      {columns.map((col) => (
        <label
          key={col}
          className={`flex items-center gap-2 px-3 py-2 rounded-lg border cursor-pointer text-sm ${
            selected.includes(col)
              ? 'border-indigo-500 bg-indigo-50 text-indigo-700'
              : 'border-slate-200 bg-white text-slate-600'
          }`}
        >
          <input
            type="checkbox"
            checked={selected.includes(col)}
            onChange={() => onToggle(col)}
            className="accent-indigo-600"
          />
          {col}
        </label>
      ))}
    </div>
  )
}
