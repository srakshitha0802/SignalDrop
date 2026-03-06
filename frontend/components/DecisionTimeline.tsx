import React, { useState, useEffect } from 'react'

interface Intervention {
  week: number
  type: string
  description: string
  risk_reduction: number
  confidence: number
}

interface DecisionTimelineData {
  current_risk: number
  projected_risk: number
  total_risk_reduction: number
  risk_reduction_percent: number
  interventions: Intervention[]
  interpretation: string
}

interface DecisionTimelineProps {
  studentId: string
  alertWeek: number
}

export default function DecisionTimeline({ studentId, alertWeek }: DecisionTimelineProps) {
  const [data, setData] = useState<DecisionTimelineData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(`/api/student/${studentId}/decision-timeline?week=${alertWeek}`)
        const result = await response.json()
        setData(result.decision_timeline)
      } catch (error) {
        console.error('Error fetching decision timeline:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [studentId, alertWeek])

  if (loading) {
    return (
      <div className="bg-gray-50 p-6 rounded-lg">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Decision Timeline</h3>
        <div className="text-gray-600">Loading decision analysis...</div>
      </div>
    )
  }

  if (!data) {
    return (
      <div className="bg-gray-50 p-6 rounded-lg">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Decision Timeline</h3>
        <div className="text-gray-600">No decision timeline available.</div>
      </div>
    )
  }

  const getRiskColor = (risk: number) => {
    if (risk < 0.3) return 'text-green-600'
    if (risk < 0.6) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence > 0.8) return 'bg-green-100 text-green-700'
    if (confidence > 0.6) return 'bg-yellow-100 text-yellow-700'
    return 'bg-red-100 text-red-700'
  }

  return (
    <div className="bg-gray-50 p-6 rounded-lg">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Decision Timeline</h3>
      
      <div className="mb-6">
        <div className="text-sm text-gray-600 mb-2">Executive View</div>
        <div className="bg-white p-4 rounded border border-gray-200">
          <div className="text-lg font-medium text-gray-900 mb-2">
            If an intervention happened at Week {alertWeek + 1}, projected risk would reduce by {data.risk_reduction_percent.toFixed(1)}%
          </div>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-600">Current Risk:</span>
              <span className={`ml-2 font-medium ${getRiskColor(data.current_risk)}`}>
                {(data.current_risk * 100).toFixed(0)}%
              </span>
            </div>
            <div>
              <span className="text-gray-600">Projected Risk:</span>
              <span className={`ml-2 font-medium ${getRiskColor(data.projected_risk)}`}>
                {(data.projected_risk * 100).toFixed(0)}%
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="mb-6">
        <h4 className="text-md font-semibold text-gray-900 mb-3">Recommended Interventions</h4>
        <div className="space-y-3">
          {data.interventions.map((intervention, index) => (
            <div key={index} className="bg-white p-3 rounded border border-gray-200">
              <div className="flex justify-between items-start mb-2">
                <div className="flex-1">
                  <div className="font-medium text-gray-900">{intervention.type}</div>
                  <div className="text-sm text-gray-600">{intervention.description}</div>
                </div>
                <div className="ml-4 text-right">
                  <div className="text-sm font-medium text-green-600">
                    -{(intervention.risk_reduction * 100).toFixed(0)}% risk
                  </div>
                  <div className={`text-xs px-2 py-1 rounded ${getConfidenceColor(intervention.confidence)}`}>
                    {(intervention.confidence * 100).toFixed(0)}% confidence
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-blue-50 p-4 rounded border border-blue-200">
        <div className="text-sm text-blue-800">
          <span className="font-medium">Decision Framing:</span> {data.interpretation}
        </div>
      </div>
    </div>
  )
}
