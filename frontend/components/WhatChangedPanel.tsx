import React, { useState, useEffect } from 'react'

interface WhatChangedData {
  analysis_period: string
  significant_changes: Array<{
    signal: string
    change: {
      from_value: number
      to_value: number
      percent_change: number
      direction: string
      magnitude: number
      signal_type: string
    }
    contribution: number
  }>
  threshold_crossing: string
  time_lag_analysis: Record<string, {
    started_changing_week: number
    alert_week: number
    lag_weeks: number
    interpretation: string
  }>
}

interface WhatChangedPanelProps {
  studentId: string
  alertWeek: number
}

export default function WhatChangedPanel({ studentId, alertWeek }: WhatChangedPanelProps) {
  const [data, setData] = useState<WhatChangedData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(`/api/student/${studentId}/what-changed?week=${alertWeek}`)
        const result = await response.json()
        setData(result.causal_analysis)
      } catch (error) {
        console.error('Error fetching what-changed data:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [studentId, alertWeek])

  if (loading) {
    return (
      <div className="bg-gray-50 p-6 rounded-lg">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">What Changed?</h3>
        <div className="text-gray-600">Loading causal analysis...</div>
      </div>
    )
  }

  if (!data) {
    return (
      <div className="bg-gray-50 p-6 rounded-lg">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">What Changed?</h3>
        <div className="text-gray-600">No causal analysis available.</div>
      </div>
    )
  }

  const formatSignalName = (signal: string) => {
    return signal.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())
  }

  const getChangeColor = (direction: string) => {
    return direction === 'decreased' ? 'text-red-600' : 'text-green-600'
  }

  const getChangeIcon = (direction: string) => {
    return direction === 'decreased' ? '↓' : '↑'
  }

  return (
    <div className="bg-gray-50 p-6 rounded-lg">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">What Changed?</h3>
      
      <div className="mb-6">
        <div className="text-sm text-gray-600 mb-2">Analysis Period</div>
        <div className="text-lg font-medium text-gray-900">{data.analysis_period}</div>
      </div>

      <div className="mb-6">
        <h4 className="text-md font-semibold text-gray-900 mb-3">Significant Changes</h4>
        <div className="space-y-3">
          {data.significant_changes.map((change, index) => (
            <div key={index} className="bg-white p-4 rounded border border-gray-200">
              <div className="flex justify-between items-start mb-2">
                <div className="font-medium text-gray-900">
                  {formatSignalName(change.signal)}
                </div>
                <div className={`text-sm font-medium ${getChangeColor(change.change.direction)}`}>
                  {getChangeIcon(change.change.direction)} {change.change.percent_change.toFixed(1)}%
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4 text-sm text-gray-600 mb-2">
                <div>
                  <span className="font-medium">From:</span> {change.change.from_value.toFixed(2)}
                </div>
                <div>
                  <span className="font-medium">To:</span> {change.change.to_value.toFixed(2)}
                </div>
              </div>
              
              <div className="text-sm text-gray-600">
                <span className="font-medium">Risk Contribution:</span> {(change.contribution * 100).toFixed(1)}%
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="mb-6">
        <h4 className="text-md font-semibold text-gray-900 mb-3">Threshold Crossing</h4>
        <div className="bg-white p-4 rounded border border-gray-200">
          <p className="text-gray-700">{data.threshold_crossing}</p>
        </div>
      </div>

      <div>
        <h4 className="text-md font-semibold text-gray-900 mb-3">Time Lag Analysis</h4>
        <div className="space-y-2">
          {Object.entries(data.time_lag_analysis).map(([signal, lag]) => (
            <div key={signal} className="bg-white p-3 rounded border border-gray-200">
              <div className="flex justify-between items-center mb-1">
                <div className="font-medium text-gray-900 text-sm">
                  {formatSignalName(signal)}
                </div>
                <div className="text-sm text-gray-600">
                  {lag.lag_weeks} weeks lag
                </div>
              </div>
              <div className="text-xs text-gray-600">
                Started changing Week {lag.started_changing_week} → Alert Week {lag.alert_week}
              </div>
              <div className="text-xs text-gray-500 mt-1 italic">
                {lag.interpretation}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
