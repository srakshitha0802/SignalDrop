import React, { useState, useEffect } from 'react'

interface CounterfactualScenario {
  scenario: string
  description: string
  risk_change: {
    from: number
    to: number
    delta: number
    percent_change: number
  }
  momentum_change: {
    from: number
    to: number
    delta: number
  }
  still_alerts: boolean
  interpretation: string
}

interface CounterfactualPanelProps {
  studentId: string
  alertWeek: number
}

export default function CounterfactualPanel({ studentId, alertWeek }: CounterfactualPanelProps) {
  const [data, setData] = useState<CounterfactualScenario[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(`/api/student/${studentId}/counterfactuals?week=${alertWeek}`)
        const result = await response.json()
        setData(result.counterfactuals)
      } catch (error) {
        console.error('Error fetching counterfactuals:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [studentId, alertWeek])

  if (loading) {
    return (
      <div className="bg-gray-50 p-6 rounded-lg">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Would This Alert Still Trigger If…?</h3>
        <div className="text-gray-600">Loading counterfactual analysis...</div>
      </div>
    )
  }

  if (!data || data.length === 0) {
    return (
      <div className="bg-gray-50 p-6 rounded-lg">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Would This Alert Still Trigger If…?</h3>
        <div className="text-gray-600">No counterfactual scenarios available.</div>
      </div>
    )
  }

  const getRiskColor = (from: number, to: number) => {
    if (to < from) return 'text-green-600'
    if (to > from) return 'text-red-600'
    return 'text-gray-600'
  }

  const getRiskIcon = (from: number, to: number) => {
    if (to < from) return '↓'
    if (to > from) return '↑'
    return '→'
  }

  const getAlertStatus = (stillAlerts: boolean) => {
    return stillAlerts ? (
      <span className="px-2 py-1 bg-red-100 text-red-700 rounded text-xs font-medium">
        Alert Still Triggers
      </span>
    ) : (
      <span className="px-2 py-1 bg-green-100 text-green-700 rounded text-xs font-medium">
        Alert Prevented
      </span>
    )
  }

  return (
    <div className="bg-gray-50 p-6 rounded-lg">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Would This Alert Still Trigger If…?</h3>
      
      <div className="space-y-4">
        {data.map((scenario, index) => (
          <div key={index} className="bg-white p-4 rounded border border-gray-200">
            <div className="flex justify-between items-start mb-3">
              <div className="flex-1">
                <h4 className="font-semibold text-gray-900 mb-1">{scenario.scenario}</h4>
                <p className="text-sm text-gray-600 mb-2">{scenario.description}</p>
              </div>
              <div className="ml-4">
                {getAlertStatus(scenario.still_alerts)}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-3">
              <div className="bg-gray-50 p-3 rounded">
                <div className="text-sm font-medium text-gray-700 mb-1">Risk Score</div>
                <div className="flex items-center justify-between">
                  <div className="text-sm text-gray-600">
                    {(scenario.risk_change.from * 100).toFixed(0)}% → {(scenario.risk_change.to * 100).toFixed(0)}%
                  </div>
                  <div className={`font-medium ${getRiskColor(scenario.risk_change.from, scenario.risk_change.to)}`}>
                    {getRiskIcon(scenario.risk_change.from, scenario.risk_change.to)} {scenario.risk_change.percent_change > 0 ? '+' : ''}{scenario.risk_change.percent_change.toFixed(1)}%
                  </div>
                </div>
              </div>

              <div className="bg-gray-50 p-3 rounded">
                <div className="text-sm font-medium text-gray-700 mb-1">Risk Momentum</div>
                <div className="flex items-center justify-between">
                  <div className="text-sm text-gray-600">
                    {scenario.momentum_change.from.toFixed(3)} → {scenario.momentum_change.to.toFixed(3)}
                  </div>
                  <div className={`font-medium ${getRiskColor(scenario.momentum_change.from, scenario.momentum_change.to)}`}>
                    {getRiskIcon(scenario.momentum_change.from, scenario.momentum_change.to)} {scenario.momentum_change.delta > 0 ? '+' : ''}{scenario.momentum_change.delta.toFixed(3)}
                  </div>
                </div>
              </div>
            </div>

            <div className="text-sm text-gray-700 italic">
              <span className="font-medium">Interpretation:</span> {scenario.interpretation}
            </div>
          </div>
        ))}
      </div>

      <div className="mt-4 p-3 bg-blue-50 rounded border border-blue-200">
        <div className="text-sm text-blue-800">
          <span className="font-medium">Why This Matters:</span> These counterfactual scenarios show that the alert is causally grounded and not brittle. The system responds differently to various signal combinations, demonstrating genuine reasoning rather than memorization.
        </div>
      </div>
    </div>
  )
}
