import { useCallback, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { UploadCloud, FileSpreadsheet, AlertCircle } from 'lucide-react'
import { parseCSVFile } from '../utils/csvParser'
import { useAppStore } from '../store'

export default function LandingPage() {
  const navigate = useNavigate()
  const setFile = useAppStore((s) => s.setFile)
  const [error, setError] = useState<string | null>(null)
  const [isDragging, setIsDragging] = useState(false)
  const [loading, setLoading] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  const handleFile = useCallback(
    async (file: File) => {
      if (!file.name.toLowerCase().endsWith('.csv')) {
        setError('Please upload a valid .csv file.')
        return
      }
      setLoading(true)
      setError(null)
      try {
        const { rows, columns } = await parseCSVFile(file)
        if (columns.length === 0) {
          setError('The CSV file appears to be empty or invalid.')
          setLoading(false)
          return
        }
        setFile(file.name, rows, columns)
        navigate('/config')
      } catch (err) {
        setError('Failed to parse CSV file. Please check the file format.')
      } finally {
        setLoading(false)
      }
    },
    [navigate, setFile],
  )

  const onDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    setIsDragging(false)
    const file = e.dataTransfer.files?.[0]
    if (file) handleFile(file)
  }

  const onInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) handleFile(file)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-indigo-50 flex flex-col items-center justify-center px-4">
      <div className="max-w-xl w-full text-center">
        <div className="flex justify-center mb-4">
          <FileSpreadsheet className="w-12 h-12 text-indigo-600" />
        </div>
        <h1 className="text-4xl font-bold text-slate-800 mb-2">Welcome to Annotaid</h1>
        <p className="text-slate-500 mb-8">
          Upload your CSV file to get started with annotation.
        </p>

        <div
          onDragOver={(e) => {
            e.preventDefault()
            setIsDragging(true)
          }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={onDrop}
          onClick={() => inputRef.current?.click()}
          className={`cursor-pointer rounded-2xl border-2 border-dashed p-12 transition-colors ${
            isDragging
              ? 'border-indigo-500 bg-indigo-50'
              : 'border-slate-300 bg-white hover:border-indigo-400'
          }`}
        >
          <UploadCloud className="w-10 h-10 mx-auto text-indigo-500 mb-3" />
          <p className="text-slate-700 font-medium">
            {loading ? 'Loading...' : 'Drag & drop your CSV file here, or click to browse'}
          </p>
          <p className="text-slate-400 text-sm mt-1">.csv files only</p>
          <input
            ref={inputRef}
            type="file"
            accept=".csv"
            className="hidden"
            onChange={onInputChange}
          />
        </div>

        {error && (
          <div className="mt-4 flex items-center gap-2 justify-center text-red-600 bg-red-50 rounded-lg px-4 py-3">
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            <span className="text-sm">{error}</span>
          </div>
        )}
      </div>
    </div>
  )
}
