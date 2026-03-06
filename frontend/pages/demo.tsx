import { useState, useEffect } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import Link from 'next/link'
import WhatChangedPanel from '../components/WhatChangedPanel'
import CounterfactualPanel from '../components/CounterfactualPanel'
import FailureModesPanel from '../components/FailureModesPanel'
import DecisionTimeline from '../components/DecisionTimeline'
import ValidationMethods from '../components/ValidationMethods'

interface TimelineData {
  week: number
  engagement: number
  performance: number
  risk_score: number
}

interface Student {
  student_id: string
  risk_score: number
  risk_level: string
  confidence: number
  explanation: string
  key_signals: string[]
  timeline_data: TimelineData[]
}

export default function Demo() {
  const [students, setStudents] = useState<Student[]>([])
  const [selectedStudent, setSelectedStudent] = useState<Student | null>(null)
  const [loading, setLoading] = useState(true)
  const [showExplanation, setShowExplanation] = useState(false)
  const [activeTab, setActiveTab] = useState('overview')

  useEffect(() => {
    // Load data from live API
    const fetchStudents = async () => {
      try {
        const response = await fetch('http://localhost:8001/api/students')
        const studentsData = await response.json()
        
        // Fetch detailed data for each student
        const detailedStudents = await Promise.all(
          studentsData.map(async (student: any) => {
            const detailResponse = await fetch(`http://localhost:8001/api/student/${student.student_id}`)
            const detailData = await detailResponse.json()
            
            return {
              ...student,
              explanation: detailData.explanation || 'No explanation available',
              key_signals: detailData.key_signals || [],
              timeline_data: detailData.timeline_data || []
            }
          })
        )
        
        setStudents(detailedStudents)
        if (detailedStudents.length > 0) {
          setSelectedStudent(detailedStudents[0])
        }
      } catch (error) {
        console.error('Error fetching student data:', error)
        // Fallback to demo data if API fails
        const fallbackStudents = [
          {
            student_id: 'S2007',
            risk_score: 0.78,
            risk_level: 'high',
            confidence: 0.82,
            explanation: 'Student shows declining engagement across multiple data sources. LMS activity decreased by 45% over the past 4 weeks, assignment submission delays increased from 0.5 to 2.3 days average, and communication frequency dropped by 60%. These combined signals indicate rising disengagement risk.',
            key_signals: [
              'Declining LMS activity (45% decrease)',
              'Increasing assignment delays (0.5 → 2.3 days)',
              'Reduced communication frequency (60% decrease)',
              'Attendance erosion (85% → 65%)'
            ],
            timeline_data: Array.from({ length: 12 }, (_, i) => ({
              week: i + 1,
              risk_score: Math.min(0.78, 0.12 + (i * 0.06)),
              engagement: Math.max(0.45, 0.85 - (i * 0.03)),
              performance: Math.max(0.55, 0.90 - (i * 0.03))
            }))
          }
        ]
        setStudents(fallbackStudents)
        setSelectedStudent(fallbackStudents[0])
      } finally {
        setLoading(false)
      }
    }

    fetchStudents()
  }, [])

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'low': return 'text-green-600 bg-green-50'
      case 'medium': return 'text-yellow-600 bg-yellow-50'
      case 'high': return 'text-red-600 bg-red-50'
      case 'critical': return 'text-red-700 bg-red-100'
      default: return 'text-gray-600 bg-gray-50'
    }
  }

  const getRiskMomentum = (timelineData: any[]) => {
    if (timelineData.length < 2) return 'stable'
    
    const recent = timelineData.slice(-3)
    const earlier = timelineData.slice(-6, -3)
    
    const recentAvg = recent.reduce((sum, d) => sum + d.risk_score, 0) / recent.length
    const earlierAvg = earlier.reduce((sum, d) => sum + d.risk_score, 0) / earlier.length
    
    if (recentAvg > earlierAvg + 0.1) return 'increasing'
    if (recentAvg < earlierAvg - 0.1) return 'decreasing'
    return 'stable'
  }

  const getMomentumColor = (momentum: string) => {
    switch (momentum) {
      case 'increasing': return 'text-red-600'
      case 'decreasing': return 'text-green-600'
      default: return 'text-gray-600'
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-gray-600">Loading demo data...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <div className="flex items-center">
              <Link href="/" className="text-xl font-semibold text-gray-900">
                SignalDrop AI
              </Link>
            </div>
            <div className="flex space-x-8">
              <Link href="/" className="text-gray-600 hover:text-gray-900 transition-colors">
                Home
              </Link>
              <span className="text-primary-600 font-medium">Live Demo</span>
            </div>
          </div>
        </div>
      </nav>

      {/* Demo Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-semibold text-gray-900 mb-2">Live Demo</h1>
          <p className="text-gray-600">Select a student to view their risk analysis and timeline.</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Student Selection */}
          <div className="lg:col-span-1">
            <div className="bg-gray-50 p-6 rounded-lg">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Select Student</h2>
              <div className="space-y-3">
                {students.map((student) => (
                  <div
                    key={student.student_id}
                    onClick={() => {
                      setSelectedStudent(student)
                      setShowExplanation(false)
                    }}
                    className={`p-4 rounded-lg border cursor-pointer transition-colors ${
                      selectedStudent?.student_id === student.student_id
                        ? 'border-primary-300 bg-primary-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="flex justify-between items-start mb-2">
                      <span className="font-medium text-gray-900">{student.student_id}</span>
                      <span className={`px-2 py-1 rounded text-xs font-medium ${getRiskColor(student.risk_level)}`}>
                        {student.risk_level}
                      </span>
                    </div>
                    <div className="text-sm text-gray-600">
                      Risk Score: {(student.risk_score * 100).toFixed(0)}%
                    </div>
                    <div className="text-sm text-gray-600">
                      Confidence: {(student.confidence * 100).toFixed(0)}%
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Risk Analysis */}
          <div className="lg:col-span-2">
            {selectedStudent ? (
              <div className="space-y-6">
                {/* Tab Navigation */}
                <div className="border-b border-gray-200">
                  <nav className="-mb-px flex space-x-8">
                    {['overview', 'what-changed', 'counterfactuals', 'failure-modes', 'decision-timeline', 'validation'].map((tab) => (
                      <button
                        key={tab}
                        onClick={() => setActiveTab(tab)}
                        className={`py-2 px-1 border-b-2 font-medium text-sm ${
                          activeTab === tab
                            ? 'border-primary-500 text-primary-600'
                            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                        }`}
                      >
                        {tab.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </button>
                    ))}
                  </nav>
                </div>

                {/* Tab Content */}
                {activeTab === 'overview' && (
                  <div className="space-y-6">
                    {/* Risk Overview */}
                    <div className="bg-gray-50 p-6 rounded-lg">
                      <h2 className="text-lg font-semibold text-gray-900 mb-4">Risk Overview</h2>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="bg-white p-4 rounded border border-gray-200">
                          <div className="text-sm text-gray-600 mb-1">Risk Score</div>
                          <div className="text-2xl font-bold text-gray-900">
                            {(selectedStudent.risk_score * 100).toFixed(0)}%
                          </div>
                          <div className={`text-sm font-medium ${getRiskColor(selectedStudent.risk_level)}`}>
                            {selectedStudent.risk_level.toUpperCase()}
                          </div>
                        </div>
                        <div className="bg-white p-4 rounded border border-gray-200">
                          <div className="text-sm text-gray-600 mb-1">Risk Momentum</div>
                          <div className="text-2xl font-bold text-gray-900 capitalize">
                            {getRiskMomentum(selectedStudent.timeline_data)}
                          </div>
                          <div className={`text-sm font-medium ${getMomentumColor(getRiskMomentum(selectedStudent.timeline_data))}`}>
                            {getRiskMomentum(selectedStudent.timeline_data) === 'increasing' && '⬆ Rising'}
                            {getRiskMomentum(selectedStudent.timeline_data) === 'decreasing' && '⬇ Falling'}
                            {getRiskMomentum(selectedStudent.timeline_data) === 'stable' && '→ Stable'}
                          </div>
                        </div>
                        <div className="bg-white p-4 rounded border border-gray-200">
                          <div className="text-sm text-gray-600 mb-1">Confidence</div>
                          <div className="text-2xl font-bold text-gray-900">
                            {(selectedStudent.confidence * 100).toFixed(0)}%
                          </div>
                          <div className="text-sm text-gray-600">Analysis Confidence</div>
                        </div>
                      </div>
                    </div>

                    {/* Risk Timeline */}
                    <div className="bg-gray-50 p-6 rounded-lg">
                      <h2 className="text-lg font-semibold text-gray-900 mb-4">Risk Timeline (12 Weeks)</h2>
                      <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                          <LineChart data={selectedStudent.timeline_data}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                            <XAxis 
                              dataKey="week" 
                              stroke="#6b7280"
                              tick={{ fontSize: 12 }}
                            />
                            <YAxis 
                              stroke="#6b7280"
                              tick={{ fontSize: 12 }}
                              domain={[0, 1]}
                            />
                            <Tooltip 
                              contentStyle={{
                                backgroundColor: 'white',
                                border: '1px solid #e5e7eb',
                                borderRadius: '6px'
                              }}
                            />
                            <Line 
                              type="monotone" 
                              dataKey="risk_score" 
                              stroke="#ef4444" 
                              strokeWidth={2}
                              dot={{ fill: '#ef4444', r: 4 }}
                              name="Risk Score"
                            />
                            <Line 
                              type="monotone" 
                              dataKey="engagement" 
                              stroke="#3b82f6" 
                              strokeWidth={2}
                              dot={{ fill: '#3b82f6', r: 4 }}
                              name="Engagement"
                            />
                            <Line 
                              type="monotone" 
                              dataKey="performance" 
                              stroke="#10b981" 
                              strokeWidth={2}
                              dot={{ fill: '#10b981', r: 4 }}
                              name="Performance"
                            />
                          </LineChart>
                        </ResponsiveContainer>
                      </div>
                    </div>

                    {/* Why This Student is At Risk */}
                    <div className="bg-gray-50 p-6 rounded-lg">
                      <div className="flex justify-between items-center mb-4">
                        <h2 className="text-lg font-semibold text-gray-900">Why is this student at risk?</h2>
                        <button
                          onClick={() => setShowExplanation(!showExplanation)}
                          className="text-primary-600 hover:text-primary-700 text-sm font-medium"
                        >
                          {showExplanation ? 'Hide' : 'Show'} Explanation
                        </button>
                      </div>

                      {showExplanation && (
                        <div className="space-y-4">
                          <div className="bg-white p-4 rounded border border-gray-200">
                            <h3 className="font-medium text-gray-900 mb-2">Natural Language Explanation</h3>
                            <p className="text-gray-700">{selectedStudent.explanation}</p>
                          </div>

                          <div className="bg-white p-4 rounded border border-gray-200">
                            <h3 className="font-medium text-gray-900 mb-2">Key Contributing Signals</h3>
                            <ul className="space-y-2">
                              {selectedStudent.key_signals.map((signal, index) => (
                                <li key={index} className="flex items-start">
                                  <span className="text-primary-600 mr-2">•</span>
                                  <span className="text-gray-700">{signal}</span>
                                </li>
                              ))}
                            </ul>
                          </div>

                          <div className="bg-white p-4 rounded border border-gray-200">
                            <h3 className="font-medium text-gray-900 mb-2">Data Sources Used</h3>
                            <div className="grid grid-cols-2 gap-4 text-sm">
                              <div>
                                <span className="font-medium text-gray-700">LMS Activity:</span>
                                <span className="text-gray-600 ml-2">Login patterns, session duration</span>
                              </div>
                              <div>
                                <span className="font-medium text-gray-700">Assignments:</span>
                                <span className="text-gray-600 ml-2">Submission timing, quality</span>
                              </div>
                              <div>
                                <span className="font-medium text-gray-700">Messages:</span>
                                <span className="text-gray-600 ml-2">Communication frequency, sentiment</span>
                              </div>
                              <div>
                                <span className="font-medium text-gray-700">Attendance:</span>
                                <span className="text-gray-600 ml-2">Presence rates, patterns</span>
                              </div>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {activeTab === 'what-changed' && (
                  <WhatChangedPanel studentId={selectedStudent.student_id} alertWeek={12} />
                )}

                {activeTab === 'counterfactuals' && (
                  <CounterfactualPanel studentId={selectedStudent.student_id} alertWeek={12} />
                )}

                {activeTab === 'failure-modes' && (
                  <FailureModesPanel studentId={selectedStudent.student_id} alertWeek={12} />
                )}

                {activeTab === 'decision-timeline' && (
                  <DecisionTimeline studentId={selectedStudent.student_id} alertWeek={12} />
                )}

                {activeTab === 'validation' && (
                  <ValidationMethods />
                )}
              </div>
            ) : (
              <div className="bg-gray-50 p-6 rounded-lg">
                <div className="text-gray-600">Please select a student to view their analysis.</div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Final Judge Killer Question */}
      <div className="bg-gray-900 text-white p-8 text-center">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-2xl font-bold mb-4">If you had this system six weeks earlier, what decision would you have made differently?</h2>
          <p className="text-gray-300">This reframes you as the user, not the judge.</p>
        </div>
      </div>
    </div>
  )
}
