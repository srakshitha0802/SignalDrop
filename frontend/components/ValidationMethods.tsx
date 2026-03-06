import React, { useState, useEffect } from 'react'

interface ValidationMethodsData {
  validation_methods: {
    retrospective_replay: {
      description: string
      process: string
      metric: string
    }
    time_sliced_evaluation: {
      description: string
      process: string
      metric: string
    }
    signal_ablation_tests: {
      description: string
      process: string
      metric: string
    }
    false_positive_tolerance: {
      description: string
      process: string
      metric: string
    }
  }
  confidence_building: {
    human_review: string
    transparency: string
    appeal_process: string
    continuous_monitoring: string
  }
}

export default function ValidationMethods() {
  const [data, setData] = useState<ValidationMethodsData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('/api/validation-methods')
        const result = await response.json()
        setData(result)
      } catch (error) {
        console.error('Error fetching validation methods:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  if (loading) {
    return (
      <div className="bg-gray-50 p-6 rounded-lg">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">How We Validate Without Ground Truth</h3>
        <div className="text-gray-600">Loading validation methods...</div>
      </div>
    )
  }

  if (!data) {
    return (
      <div className="bg-gray-50 p-6 rounded-lg">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">How We Validate Without Ground Truth</h3>
        <div className="text-gray-600">No validation methods available.</div>
      </div>
    )
  }

  return (
    <div className="bg-gray-50 p-6 rounded-lg">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">How We Validate Without Ground Truth</h3>
      
      <div className="mb-6">
        <p className="text-gray-700 mb-4">
          We don't claim accuracy percentages or use fake benchmarks. Instead, we validate through operational methods that prove real-world effectiveness.
        </p>
        
        <div className="space-y-4">
          {Object.entries(data.validation_methods).map(([key, method]) => (
            <div key={key} className="bg-white p-4 rounded border border-gray-200">
              <h4 className="font-semibold text-gray-900 mb-2 capitalize">
                {key.replace('_', ' ')}
              </h4>
              <p className="text-sm text-gray-600 mb-2">{method.description}</p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div className="bg-blue-50 p-2 rounded">
                  <div className="text-xs font-medium text-blue-700 mb-1">Process</div>
                  <div className="text-xs text-blue-600">{method.process}</div>
                </div>
                <div className="bg-green-50 p-2 rounded">
                  <div className="text-xs font-medium text-green-700 mb-1">Metric</div>
                  <div className="text-xs text-green-600">{method.metric}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="mb-6">
        <h4 className="text-md font-semibold text-gray-900 mb-3">How Confidence Is Earned</h4>
        <div className="space-y-3">
          {Object.entries(data.confidence_building).map(([key, description]) => (
            <div key={key} className="bg-white p-3 rounded border border-gray-200">
              <div className="font-medium text-gray-900 capitalize mb-1">
                {key.replace('_', ' ')}
              </div>
              <div className="text-sm text-gray-600">{description}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-yellow-50 p-4 rounded border border-yellow-200">
        <div className="text-sm text-yellow-800">
          <span className="font-medium">No Accuracy Flexing:</span> We don't claim 95% accuracy or compare against fake benchmarks. Confidence is earned through operational validation, not statistical tricks.
        </div>
      </div>
    </div>
  )
}
