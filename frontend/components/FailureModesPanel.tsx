import React, { useState, useEffect } from 'react'

interface FailureMode {
  type: string
  description: string
  impact: string
  mitigation: string
}

interface FailureModesData {
  failure_modes: FailureMode[]
  overall_uncertainty: number
  human_review_required: boolean
  confidence_adjustment: number
}

interface FailureModesPanelProps {
  studentId: string
  alertWeek: number
}

export default function FailureModesPanel({ studentId, alertWeek }: FailureModesPanelProps) {
  const [data, setData] = useState<FailureModesData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(`/api/student/${studentId}/failure-modes?week=${alertWeek}`)
        const result = await response.json()
        setData(result.failure_modes)
      } catch (error) {
        console.error('Error fetching failure modes:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [studentId, alertWeek])

  if (loading) {
    return (
      <div className="bg-gray-50 p-6 rounded-lg">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">When SignalDrop AI Can Be Wrong</h3>
        <div className="text-gray-600">Loading failure mode analysis...</div>
      </div>
    )
  }

  if (!data) {
    return (
      <div className="bg-gray-50 p-6 rounded-lg">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">When SignalDrop AI Can Be Wrong</h3>
        <div className="text-gray-600">No failure mode analysis available.</div>
      </div>
    )
  }

  const getUncertaintyColor = (uncertainty: number) => {
    if (uncertainty < 0.3) return 'text-green-600'
    if (uncertainty < 0.6) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getUncertaintyLabel = (uncertainty: number) => {
    if (uncertainty < 0.3) return 'Low'
    if (uncertainty < 0.6) return 'Medium'
    return 'High'
  }

  const getFailureModeIcon = (type: string) => {
    switch (type) {
      case 'Sparse Data': return '📊'
      case 'Behavioral Shock': return '⚡'
      case 'Adversarial Inputs': return '🛡️'
      case 'Cold Start': return '❄️'
      default: return '⚠️'
    }
  }

  return (
    <div className="bg-gray-50 p-6 rounded-lg">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">When SignalDrop AI Can Be Wrong</h3>
      
      <div className="mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div className="bg-white p-4 rounded border border-gray-200">
            <div className="text-sm text-gray-600 mb-1">Overall Uncertainty</div>
            <div className={`text-lg font-bold ${getUncertaintyColor(data.overall_uncertainty)}`}>
              {(data.overall_uncertainty * 100).toFixed(0)}%
            </div>
            <div className="text-sm text-gray-600">{getUncertaintyLabel(data.overall_uncertainty)}</div>
          </div>
          
          <div className="bg-white p-4 rounded border border-gray-200">
            <div className="text-sm text-gray-600 mb-1">Confidence Adjustment</div>
            <div className={`text-lg font-bold ${getUncertaintyColor(1 - data.confidence_adjustment)}`}>
              {(data.confidence_adjustment * 100).toFixed(0)}%
            </div>
            <div className="text-sm text-gray-600">Adjusted Confidence</div>
          </div>
          
          <div className="bg-white p-4 rounded border border-gray-200">
            <div className="text-sm text-gray-600 mb-1">Human Review</div>
            <div className={`text-lg font-bold ${data.human_review_required ? 'text-red-600' : 'text-green-600'}`}>
              {data.human_review_required ? 'Required' : 'Optional'}
            </div>
            <div className="text-sm text-gray-600">Review Status</div>
          </div>
        </div>
      </div>

      {data.failure_modes.length > 0 ? (
        <div className="space-y-4">
          <h4 className="text-md font-semibold text-gray-900">Identified Risk Factors</h4>
          {data.failure_modes.map((mode, index) => (
            <div key={index} className="bg-white p-4 rounded border border-gray-200">
              <div className="flex items-start mb-2">
                <div className="text-2xl mr-3">{getFailureModeIcon(mode.type)}</div>
                <div className="flex-1">
                  <h5 className="font-semibold text-gray-900 mb-1">{mode.type}</h5>
                  <p className="text-sm text-gray-600 mb-2">{mode.description}</p>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <div className="bg-red-50 p-2 rounded">
                      <div className="text-xs font-medium text-red-700 mb-1">Impact</div>
                      <div className="text-xs text-red-600">{mode.impact}</div>
                    </div>
                    
                    <div className="bg-blue-50 p-2 rounded">
                      <div className="text-xs font-medium text-blue-700 mb-1">Mitigation</div>
                      <div className="text-xs text-blue-600">{mode.mitigation}</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-green-50 p-4 rounded border border-green-200">
          <div className="text-green-800">
            <span className="font-medium">No significant failure modes detected.</span> The system has high confidence in this assessment.
          </div>
        </div>
      )}

      <div className="mt-6 p-4 bg-yellow-50 rounded border border-yellow-200">
        <div className="text-sm text-yellow-800">
          <span className="font-medium">Engineering Transparency:</span> We explicitly document when and how the system can be wrong. This isn't weakness—it's maturity. Every system has limitations; we make them visible and actionable.
        </div>
      </div>
    </div>
  )
}
